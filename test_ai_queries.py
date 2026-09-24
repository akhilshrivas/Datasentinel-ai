import os
os.environ["EXECUTION_MODE"] = "fabric"
from agents.orchestrator import investigate_incident
import json

def test_queries():
    queries = [
        "What happened in the latest pipeline run?",
        "How many anomalies are present?",
        "What is the recent revenue trend?"
    ]
    
    print("--- STARTING TESTS ---")
    for q in queries:
        print(f"\\nQUERY: {q}")
        res = investigate_incident(q)
        print("REPLY:")
        print(res["reply"])
        print("TOOL CALLS:")
        print(json.dumps(res["tool_calls"], indent=2))
        
        # Assertions
        assert "<think>" not in res["reply"], "Thinking leaked into reply"
        assert len(res["tool_calls"]) == 1, "Expected exactly 1 tool call"
        
    print("\\nSUCCESS: All tests passed!")

if __name__ == "__main__":
    test_queries()
