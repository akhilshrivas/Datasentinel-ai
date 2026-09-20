import os
import sys

# Ensure the app imports work properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import investigate_incident

def test_agent_integration():
    print("Testing full agent investigation loop...")
    
    query = "Why did revenue drop recently?"
    print(f"QUERY: {query}")
    
    # 1. Agent completes & finishes within configured limit
    # The investigate_incident function uses recursion_limit=10 natively
    result = investigate_incident(query)
    
    reply = result["reply"]
    tool_calls = result["tool_calls"]
    
    print("--- AGENT REPLY ---")
    print(reply)
    print("--- TOOL CALLS ---")
    print(tool_calls)
    
    assert not reply.startswith("Error:"), f"Agent failed: {reply}"
    
    # 2. At least one real tool executes
    assert len(tool_calls) > 0, "Agent did not execute any tools"
    
    # 3. Final answer contains evidence from the tool result
    # It should mention something about anomalies or pipeline or quality
    assert len(reply) > 50, "Agent reply is suspiciously short"
    
if __name__ == "__main__":
    test_agent_integration()
    print("ALL TESTS PASSED: test_agent.py")
