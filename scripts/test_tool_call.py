from langchain_core.tools import tool
from langchain_ollama import ChatOllama


@tool
def get_latest_anomalies() -> str:
    """Get the latest detected data anomalies."""
    return "Revenue anomaly detected: revenue is 31.4% below the recent baseline."


llm = ChatOllama(
    model="qwen3:4b",
    base_url="http://localhost:11434",
    temperature=0,
)

llm_with_tools = llm.bind_tools([get_latest_anomalies])

response = llm_with_tools.invoke(
    "Check whether there are recent anomalies."
)

print("CONTENT:")
print(response.content)

print("\nTOOL CALLS:")
print(response.tool_calls)

if not response.tool_calls:
    raise SystemExit(
        "FAILED: The model did not return a structured tool call."
    )

print("\nSUCCESS: Structured tool call received.")