import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage
from agents.orchestrator import investigate_incident

def test_successful_evidence_based_response():
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    mock_llm.invoke.side_effect = [
        AIMessage(content="", tool_calls=[{"name": "get_anomalies_tool", "args": {}, "id": "1"}]),
        AIMessage(content="The tool found an anomaly with value -15.5.")
    ]
    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        result = investigate_incident("Why did revenue drop yesterday?")
        reply = result["reply"]
        assert "I should call" not in reply
        assert "Wait" not in reply
        assert "-15.5" in reply or "15.5" in reply
        assert len(result["tool_calls"]) > 0

def test_insufficient_evidence():
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    # Simulate the model outputting something that gets caught by the fallback
    mock_llm.invoke.side_effect = [
        AIMessage(content="", tool_calls=[{"name": "get_anomalies_tool", "args": {}, "id": "1"}]),
        AIMessage(content="There are no_anomalies found.")
    ]
    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        result = investigate_incident("Why did revenue drop yesterday?")
        reply = result["reply"]
        assert "insufficient to determine the root cause" in reply.lower()
        assert "I should call" not in reply

def test_no_hallucinated_metrics():
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    mock_llm.invoke.side_effect = [
        AIMessage(content="", tool_calls=[{"name": "get_anomalies_tool", "args": {}, "id": "1"}]),
        AIMessage(content="The metric value is 5.0")
    ]
    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        result = investigate_incident("Why did revenue drop yesterday?")
        reply = result["reply"]
        assert "20%" not in reply
        assert "1000" not in reply
        assert "5.0" in reply or "5" in reply

def test_stale_pipeline_metadata():
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    mock_llm.invoke.side_effect = [
        AIMessage(content="", tool_calls=[{"name": "check_data_freshness_tool", "args": {"anomaly_timestamp": "2023-10-25T10:00:00Z"}, "id": "1"}]),
        AIMessage(content="The pipeline is STALE. The last run was 2023-10-24.")
    ]
    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        result = investigate_incident("Check if the data is fresh for the 2023-10-25 anomaly.")
        reply = result["reply"]
        assert "STALE" in reply or "stale" in reply.lower()
        assert "2023-10-24" in reply

def test_anomaly_pipeline_timestamp_mismatch():
    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm
    mock_llm.invoke.side_effect = [
        AIMessage(content="", tool_calls=[{"name": "check_data_freshness_tool", "args": {"anomaly_timestamp": "2023-10-25T10:00:00Z"}, "id": "1"}]),
        AIMessage(content="The pipeline is FRESH.")
    ]
    with patch("agents.orchestrator.get_llm") as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        result = investigate_incident("Is the data fresh for the 2023-10-25 anomaly?")
        reply = result["reply"]
        assert "FRESH" in reply or "fresh" in reply.lower()
