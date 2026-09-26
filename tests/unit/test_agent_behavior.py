import pytest
from agents.orchestrator import route_query, investigate_incident

def test_deterministic_routing_pipeline():
    # Should route strictly to pipeline tool
    route = route_query("What happened in the latest pipeline run?")
    assert route is not None
    assert route["tool_name"] == "get_pipeline_status_tool"

def test_deterministic_routing_anomalies():
    # Should route strictly to anomaly tool
    route = route_query("How many anomalies are present?")
    assert route is not None
    assert route["tool_name"] == "get_anomalies_tool"

def test_deterministic_routing_metrics():
    # Should route strictly to revenue/metrics tool
    route = route_query("Show me the recent revenue trend.")
    assert route is not None
    assert route["tool_name"] == "get_revenue_and_metrics_tool"

def test_investigate_incident_deterministic_pipeline():
    # Mocking or expecting native deterministic response without LLM
    result = investigate_incident("What happened in the latest pipeline run?")
    assert "reply" in result
    assert "tool_calls" in result
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["name"] == "get_pipeline_status_tool"
    assert "<think>" not in result["reply"]

def test_investigate_incident_deterministic_anomalies():
    result = investigate_incident("How many anomalies are present?")
    assert "reply" in result
    assert "tool_calls" in result
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["name"] == "get_anomalies_tool"
    assert "<think>" not in result["reply"]
