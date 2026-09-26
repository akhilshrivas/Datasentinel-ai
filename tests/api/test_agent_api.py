import pytest
import os
from fastapi.testclient import TestClient

os.environ["EXECUTION_MODE"] = "fabric"
os.environ["FABRIC_SERVER"] = "test"
os.environ["FABRIC_DATABASE"] = "test"
os.environ["FABRIC_TENANT_ID"] = "test"
os.environ["FABRIC_WORKSPACE_ID"] = "test"
os.environ["FABRIC_EVENTHOUSE_ID"] = "test"
os.environ["FABRIC_PIPELINE_ID"] = "test"
os.environ["FABRIC_KQL_DATABASE"] = "test"

from apps.api.main import app

client = TestClient(app)

def test_agent_chat_success():
    # Because of deterministic routing, we can call the API and it will return a real result without LLM overhead.
    response = client.post("/agent/chat", json={"query": "How is the pipeline?"})
    
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "tool_calls" in data
    assert len(data["tool_calls"]) == 1
    assert data["tool_calls"][0]["name"] == "get_pipeline_status_tool"
