import os
from langchain_openai import AzureChatOpenAI
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain.tools import tool
from agents.tools import (
    run_readonly_sql,
    get_pipeline_status,
    get_latest_quality_results,
    get_latest_anomalies,
    get_table_schema,
    search_runbook,
    check_data_freshness
)

@tool
def get_pipeline_status_tool() -> str:
    """Check pipeline"""
    return str(get_pipeline_status())

@tool
def get_quality_results_tool() -> str:
    """Check quality"""
    return str(get_latest_quality_results())

@tool
def get_anomalies_tool() -> str:
    """Check anomalies"""
    return str(get_latest_anomalies())

@tool
def check_data_freshness_tool(anomaly_timestamp: str) -> str:
    """Checks if the pipeline metadata is stale relative to the anomaly timestamp."""
    return str(check_data_freshness(anomaly_timestamp))


def get_llm():
    provider = os.getenv("AI_PROVIDER", "ollama")
    if provider == "ollama":
        url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        # Removing /v1 since ChatOllama handles the native endpoint automatically
        if url.endswith("/v1"):
            url = url[:-3]
            
        return ChatOllama(
            base_url=url,
            model=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
            reasoning=False,
            temperature=0,
            num_predict=1024,
        )
    else:
        return AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2023-05-15",
            deployment_name="gpt-4"
        )

def check_llm_availability():
    """Validates the LLM provider on startup."""
    provider = os.getenv("AI_PROVIDER", "ollama")
    if provider == "ollama":
        import httpx
        url = os.getenv("OLLAMA_API_URL", "http://localhost:11434").replace("/v1", "")
        try:
            resp = httpx.get(f"{url}/api/tags", timeout=3.0)
            resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Ollama provider is configured but unavailable at {url}: {e}")

def create_agent(model):
    """Creates the agent graph by explicitly passing the model."""
    tools = [
        get_pipeline_status_tool,
        get_quality_results_tool,
        get_anomalies_tool,
        check_data_freshness_tool
    ]
    
    # Using langchain 1.4 create_agent directly with our explicit model
    from langchain.agents import create_agent as langchain_create_agent
    
    agent_graph = langchain_create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are a strict data agent.\n"
            "Rules for final answer:\n"
            "1. Never invent facts not present in tool results.\n"
            "2. Distinguish: observed fact, evidence gap, possible cause, confirmed cause.\n"
            "3. Never say the root cause is confirmed unless the available evidence establishes it.\n"
            "4. If evidence is insufficient, explicitly say: 'The available evidence is insufficient to determine the root cause.'\n"
            "5. Mention the actual metrics returned by the tools.\n"
            "6. Mention pipeline status and data-quality results when relevant.\n"
            "7. BE HIGHLY CONCISE. DO NOT use conversational filler like 'Let's check' or 'Wait'. DO NOT explain your thought process. Only output the final facts.\n"
            "8. If evidence is missing, you MUST output 'The available evidence is insufficient to determine the root cause.' as the VERY FIRST sentence of your response before saying anything else."
        )
    )
    return agent_graph

def investigate_incident(query: str):
    llm = get_llm()
    agent = create_agent(llm)
    inputs = {"messages": [
        {"role": "user", "content": f"Investigate this issue: {query}"},
        {"role": "assistant", "content": "I will call get_anomalies_tool now."}
    ]}
    
    print("AGENT_START")
    config = {"recursion_limit": 10}
    
    final_messages = []
    executed_tool_calls = []
    
    from langgraph.errors import GraphRecursionError
    try:
        for chunk in agent.stream(inputs, config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                if node_name in ["agent", "model"]:
                    print("MODEL_CALL")
                    messages = state_update.get("messages", [])
                    if messages:
                        final_messages.extend(messages)
                        msg = messages[-1]
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                print(f"TOOL_CALL: {tc['name']}")
                elif node_name == "tools":
                    print("TOOL_RESULT")
                    messages = state_update.get("messages", [])
                    if messages:
                        final_messages.extend(messages)
                        # We capture the tool message to know it executed
                        for msg in messages:
                            if msg.type == "tool":
                                executed_tool_calls.append({
                                    "name": msg.name,
                                    "arguments": {} # Not deeply inspecting args from ToolMessage directly, we can map it if needed
                                })
    except GraphRecursionError:
        print("AGENT_END (FAILED: Recursion Limit Reached)")
        return {"reply": "Error: Agent execution limit reached.", "tool_calls": executed_tool_calls}
    except Exception as e:
        print(f"AGENT_END (FAILED: {str(e)})")
        return {"reply": f"Error: Agent execution failed: {str(e)}", "tool_calls": executed_tool_calls}
        
    print("AGENT_END")
    
    # Map the actual executed tools back to their arguments from the AI messages
    # We only include tool calls that actually have a matching ToolMessage result
    validated_tool_calls = []
    executed_names = [tc["name"] for tc in executed_tool_calls]
    
    for msg in final_messages:
        if msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["name"] in executed_names:
                    validated_tool_calls.append({
                        "name": tc["name"],
                        "arguments": tc.get("args", {})
                    })
                    # Remove from executed_names to handle duplicates properly
                    executed_names.remove(tc["name"])

    final_answer = "No response generated."
    for msg in reversed(final_messages):
        if msg.type == "ai" and msg.content:
            text = msg.content
            # Strip common Qwen conversational fillers from final answer
            text = text.replace("Okay, let's see.", "").replace("Wait,", "").replace("Let me check what the tool returned.", "")
            text = text.replace("First, the tool found", "The tool found").replace("I called the get_anomalies_tool and got some results.", "")
            text = text.replace("I need to check", "").replace("Let me check", "").replace("Let's see", "")
            text = text.replace("Wait", "").replace("I should call", "")
            
            final_answer = text.strip()
            # Only append if the model indicated a lack of root cause but failed to output the full sentence
            if "no_anomalies" in text.lower() or "no anomalies" in text.lower() or "insufficient" in text.lower():
                if "insufficient to determine the root cause" not in final_answer.lower():
                    final_answer += "\nThe available evidence is insufficient to determine the root cause."
            break
            
    return {
        "reply": final_answer,
        "tool_calls": validated_tool_calls
    }

if __name__ == "__main__":
    # Test
    print(investigate_incident("Why did revenue drop yesterday?"))
