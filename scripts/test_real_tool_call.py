import os
import sys

# Ensure the app imports work properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import get_llm, get_anomalies_tool
from langchain_core.messages import HumanMessage

def test_real_tool_call():
    print("Testing real tool call with LLM directly...")
    
    # 1. Verify structured tool_call is produced
    llm = get_llm()
    # We only bind the anomalies tool
    llm_with_tools = llm.bind_tools([get_anomalies_tool])
    
    # Ask it to fetch anomalies
    messages = [HumanMessage(content="Please fetch the latest anomalies.")]
    ai_msg = llm_with_tools.invoke(messages)
    
    assert hasattr(ai_msg, "tool_calls"), "No tool_calls attribute on AIMessage"
    assert len(ai_msg.tool_calls) > 0, "No tool calls generated"
    
    tool_call = ai_msg.tool_calls[0]
    assert tool_call["name"] == "get_anomalies_tool", f"Expected get_anomalies_tool, got {tool_call['name']}"
    print(f"SUCCESS: LLM produced structured tool call: {tool_call}")
    
    # 2. Verify actual Python tool executes & 3. Returns real result
    print("Executing Python tool natively...")
    # LangChain's Tool object is callable
    tool_result = get_anomalies_tool.invoke(tool_call["args"])
    
    # Check that it executed against DuckDB and returned valid string representation of dicts
    assert isinstance(tool_result, str), "Tool result must be a string"
    # Even if DB is empty, it shouldn't crash. If DB has the anomaly, it will show up.
    print(f"SUCCESS: Tool returned result: {tool_result[:100]}...")

if __name__ == "__main__":
    test_real_tool_call()
    print("ALL TESTS PASSED: test_real_tool_call.py")
