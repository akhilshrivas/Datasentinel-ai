import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage, ToolMessage

from apps.api.main import app

client = TestClient(app)

def test_agent_chat_success():
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    
    tool_call = {"name": "get_pipeline_status_tool", "args": {}, "id": "call_abc123"}
    mock_msg1 = AIMessage(content="", tool_calls=[tool_call])
    mock_msg2 = AIMessage(content="The pipeline is healthy.")
    
    mock_llm.invoke.side_effect = [mock_msg1, mock_msg2]

    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        
        response = client.post("/agent/chat", json={"query": "How is the pipeline?"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "The pipeline is healthy."
        
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["name"] == "get_pipeline_status_tool"

def test_agent_chat_exception_handling():
    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.side_effect = Exception("LLM Timeout")
        mock_get_llm.return_value = mock_llm
        
        response = client.post("/agent/chat", json={"query": "Will fail"})
        
        assert response.status_code == 500
        assert "Agent execution failed: LLM Timeout" in response.json()["detail"]
