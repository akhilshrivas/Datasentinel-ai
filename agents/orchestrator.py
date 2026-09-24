import os
import re
import time
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI
from langchain.agents import create_agent as langchain_create_agent
from langchain.tools import tool
from langgraph.errors import GraphRecursionError

from agents.tools import (
    get_pipeline_status,
    get_latest_quality_results,
    get_latest_anomalies,
    get_revenue_and_metrics,
    get_platform_summary
)

# ---
# Readonly Tools
# ---

@tool
def get_pipeline_status_tool() -> str:
    """Check pipeline"""
    return get_pipeline_status()

@tool
def get_quality_results_tool() -> str:
    """Check quality"""
    return get_latest_quality_results()

@tool
def get_anomalies_tool() -> str:
    """Check anomalies"""
    return get_latest_anomalies()

@tool
def get_revenue_and_metrics_tool() -> str:
    """Check revenue and business metrics"""
    return get_revenue_and_metrics()

@tool
def get_platform_summary_tool() -> str:
    """Check overall platform summary"""
    return get_platform_summary()


def get_llm():
    provider = os.getenv("AI_PROVIDER", "ollama")
    if provider == "ollama":
        url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
        if url.endswith("/v1"):
            url = url[:-3]
        return ChatOllama(
            base_url=url,
            model=os.getenv("OLLAMA_MODEL", "qwen3:4b"),
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
    provider = os.getenv("AI_PROVIDER", "ollama")
    if provider == "ollama":
        import httpx
        url = os.getenv("OLLAMA_API_URL", "http://localhost:11434").replace("/v1", "")
        try:
            resp = httpx.get(f"{url}/api/tags", timeout=3.0)
            resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(f"Ollama provider is configured but unavailable at {url}: {e}")

# ---
# Sanitization
# ---

def strip_reasoning(text: str) -> str:
    """Strictly remove think blocks and reasoning traces."""
    if not text:
        return ""
    
    match = re.search(r'<ANSWER>(.*?)</ANSWER>', text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
        
    text = re.sub(r'<think>.*?(</think>|$)', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    thinking_patterns = [
        r'^(Hmm|Okay|Let me|First,? I|I need to|Wait|So,? the|Alright|We are|Based on).*?(?=\n\n|\n[A-Z]|$)',
        r'To answer this question, I need to.*?(?=\n\n|$)',
        r'I should call the .*? tool.*?(?=\n\n|$)',
        r'Calling tool.*?(?=\n\n|$)',
        r'Let\'s look at the.*?(?=\n\n|$)',
        r'I will use the.*?(?=\n\n|$)',
        r'The user wants to know.*?(?=\n\n|$)',
        r'Based on the tool output,.*?\n'
    ]
    for pattern in thinking_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    return text

# ---
# Deterministic Routing
# ---

def route_query(query: str):
    q = query.lower()
    if "pipeline" in q:
        return {"tool_name": "get_pipeline_status_tool", "tool_fn": get_pipeline_status}
    if "anomal" in q:
        return {"tool_name": "get_anomalies_tool", "tool_fn": get_latest_anomalies}
    if "revenue" in q or "metric" in q or "order" in q:
        return {"tool_name": "get_revenue_and_metrics_tool", "tool_fn": get_revenue_and_metrics}
    if "quality" in q:
        return {"tool_name": "get_quality_results_tool", "tool_fn": get_latest_quality_results}
    if "summary" in q or "platform" in q:
        return {"tool_name": "get_platform_summary_tool", "tool_fn": get_platform_summary}
    return None

def _fallback_summary(tool_name, tool_data):
    if isinstance(tool_data, list):
        count = len(tool_data)
        if tool_name == "get_pipeline_status_tool":
            if not tool_data: return "No pipeline runs found."
            def parse_time(ts):
                if not ts: return datetime.min
                try: return datetime.fromisoformat(ts[:19].replace("Z", ""))
                except Exception: return datetime.min
            
            sorted_runs = sorted([r for r in tool_data if isinstance(r, dict)], 
                               key=lambda x: parse_time(x.get("start_time")), reverse=True)
            if not sorted_runs: return "No valid pipeline runs found."
            
            latest = sorted_runs[0]
            start_dt = parse_time(latest.get("start_time"))
            fmt_time = start_dt.strftime("%I:%M:%S %p") if start_dt != datetime.min else "Unknown time"
            
            status = latest.get("status", "Unknown")
            msg = f"The latest pipeline run started at {fmt_time} and {status.lower()}."
            
            if status == "Failed":
                reason = latest.get("failure_reason", {})
                if isinstance(reason, dict): reason = reason.get("message", "Unknown error")
                msg += f" Failure reason: {reason}"
                
            prev_failed = [r for r in sorted_runs[1:] if r.get("status") == "Failed"]
            if prev_failed and status != "Failed":
                prev_reason = prev_failed[0].get("failure_reason", {})
                if isinstance(prev_reason, dict): prev_reason = prev_reason.get("message", "Unknown")
                short_reason = "Spark capacity limit" if "capacity" in str(prev_reason).lower() else str(prev_reason)[:100]
                msg += f" (Note: A previous run failed due to {short_reason})."
            return msg

        elif tool_name == "get_anomalies_tool":
            return f"{count} anomalies detected in the current window."
        elif tool_name == "get_quality_results_tool":
            passed = [r for r in tool_data if isinstance(r, dict) and r.get("status") == "passed"]
            return f"{count} tables checked. {len(passed)} passed validation."
        return f"Tool returned {count} records."
    
    elif isinstance(tool_data, dict):
        if tool_name == "get_platform_summary_tool":
            return (f"Status: {tool_data.get('status', 'N/A')}\\n"
                    f"Pipelines: {tool_data.get('active_pipelines', 'N/A')}\\n"
                    f"Reliability: {tool_data.get('reliability_score', 'N/A')}%\\n"
                    f"Incident Count: {tool_data.get('incident_count', 'N/A')}")
        kpis = tool_data.get("kpis", {})
        if kpis:
            return (f"Total Orders: {kpis.get('total_orders', 'N/A')}\\n"
                    f"Revenue: ${kpis.get('total_revenue', 0):,.2f}\\n"
                    f"AOV: ${kpis.get('average_order_value', 0):,.2f}\\n"
                    f"Unique Customers: {kpis.get('unique_customers', 'N/A')}\\n"
                    f"Period: {kpis.get('period_label', 'N/A')}")
        return "Command completed successfully."
    return "Data retrieved successfully."


def _handle_routed_query(query, route, start):
    tool_name = route["tool_name"]
    try:
        tool_data = route["tool_fn"]()
    except Exception as e:
        return {"reply": f"Tool execution failed: {str(e)}", "tool_calls": [{"name": tool_name, "arguments": {}, "status": "error"}]}
    
    tool_calls = [{"name": tool_name, "arguments": {}, "status": "success"}]
    answer = _fallback_summary(tool_name, tool_data)
    return {"reply": answer, "tool_calls": tool_calls}


def _handle_agent_fallback(query, start):
    llm = get_llm()
    tools = [
        get_pipeline_status_tool,
        get_quality_results_tool,
        get_anomalies_tool,
        get_revenue_and_metrics_tool,
        get_platform_summary_tool,
    ]
    
    agent = langchain_create_agent(
        model=llm,
        tools=tools,
        prompt="You are a strict data agent. /nothinking\nCall at most ONE tool. Output ONLY the final answer."
    )
    
    inputs = {"messages": [{"role": "user", "content": query}]}
    final_messages = []
    executed_tool_calls = []
    
    try:
        for chunk in agent.stream(inputs, config={"recursion_limit": 2}, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                messages = state_update.get("messages", [])
                if messages:
                    final_messages.extend(messages)
                    if node_name == "tools":
                        for msg in messages:
                            if getattr(msg, "type", "") == "tool":
                                executed_tool_calls.append({"name": msg.name, "arguments": {}, "status": "success"})
    except GraphRecursionError:
        pass
    except Exception as e:
        return {"reply": f"Agent error: {str(e)}", "tool_calls": executed_tool_calls}

    answer = "No response generated."
    for msg in reversed(final_messages):
        if getattr(msg, "type", "") == "ai" and msg.content:
            cleaned = strip_reasoning(msg.content)
            if cleaned:
                answer = cleaned
                break
                
    return {"reply": answer, "tool_calls": executed_tool_calls}


def investigate_incident(query: str):
    start = time.time()
    route = route_query(query)
    if route:
        return _handle_routed_query(query, route, start)
    return _handle_agent_fallback(query, start)
