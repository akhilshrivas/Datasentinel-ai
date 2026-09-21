import os
import pytest
from unittest.mock import patch
from agents.orchestrator import investigate_incident

def test_successful_evidence_based_response():
    with patch("agents.orchestrator.get_latest_anomalies") as mock_anomalies, \
         patch("agents.orchestrator.get_pipeline_status") as mock_pipeline, \
         patch("agents.orchestrator.get_latest_quality_results") as mock_quality:
        
        mock_anomalies.return_value = {"status": "anomaly_detected", "metric": "revenue", "value": -15.5}
        mock_pipeline.return_value = {"status": "healthy"}
        mock_quality.return_value = {"status": "passed"}
        
        result = investigate_incident("Why did revenue drop yesterday?")
        reply = result["reply"]
        
        # Test no internal planning
        assert "I should call" not in reply
        assert "Wait" not in reply
        assert "Let me check" not in reply.lower()
        
        # Test evidence-based response mentioning the actual metric
        assert "-15.5" in reply or "15.5" in reply
        
def test_insufficient_evidence():
    with patch("agents.orchestrator.get_latest_anomalies") as mock_anomalies, \
         patch("agents.orchestrator.get_pipeline_status") as mock_pipeline, \
         patch("agents.orchestrator.get_latest_quality_results") as mock_quality:
         
        mock_anomalies.return_value = {"status": "no_anomalies"}
        mock_pipeline.return_value = {"status": "healthy"}
        mock_quality.return_value = {"status": "passed"}
        
        result = investigate_incident("Why did revenue drop yesterday?")
        reply = result["reply"]
        
        # Test insufficient evidence clause
        assert "insufficient to determine the root cause" in reply.lower()
        assert "I should call" not in reply

def test_no_hallucinated_metrics():
    with patch("agents.orchestrator.get_latest_anomalies") as mock_anomalies, \
         patch("agents.orchestrator.get_pipeline_status") as mock_pipeline, \
         patch("agents.orchestrator.get_latest_quality_results") as mock_quality:
         
        mock_anomalies.return_value = {"status": "anomaly_detected", "metric": "revenue", "value": -5.0}
        mock_pipeline.return_value = {"status": "healthy"}
        mock_quality.return_value = {"status": "passed"}
        
        result = investigate_incident("Why did revenue drop yesterday?")
        reply = result["reply"]
        
        # Test that it doesn't invent random metrics like 20% or 1000
        assert "20%" not in reply
        assert "1000" not in reply
        assert "5.0" in reply or "5" in reply

def test_stale_pipeline_metadata():
    with patch("agents.orchestrator.get_latest_anomalies") as mock_anomalies, \
         patch("agents.orchestrator.get_pipeline_status") as mock_pipeline, \
         patch("agents.orchestrator.get_latest_quality_results") as mock_quality, \
         patch("agents.orchestrator.check_data_freshness") as mock_freshness:
         
        mock_anomalies.return_value = {"status": "anomaly_detected", "metric": "revenue", "timestamp": "2023-10-25T10:00:00Z"}
        mock_pipeline.return_value = {"status": "healthy"}
        mock_quality.return_value = {"status": "passed"}
        mock_freshness.return_value = {"status": "STALE", "expected_freshness": ">= 2023-10-25T10:00:00Z", "observed_latest_run": "2023-10-24T10:00:00Z", "age_seconds": 86400}
        
        result = investigate_incident("Check if the data is fresh for the 2023-10-25 anomaly.")
        reply = result["reply"]
        
        assert "STALE" in reply or "stale" in reply.lower()
        assert "2023-10-24" in reply

def test_anomaly_pipeline_timestamp_mismatch():
    with patch("agents.orchestrator.get_latest_anomalies") as mock_anomalies, \
         patch("agents.orchestrator.get_pipeline_status") as mock_pipeline, \
         patch("agents.orchestrator.get_latest_quality_results") as mock_quality, \
         patch("agents.orchestrator.check_data_freshness") as mock_freshness:
         
        mock_anomalies.return_value = {"status": "anomaly_detected", "metric": "revenue", "timestamp": "2023-10-25T10:00:00Z"}
        mock_pipeline.return_value = {"status": "healthy"}
        mock_quality.return_value = {"status": "passed"}
        mock_freshness.return_value = {"status": "FRESH"}
        
        result = investigate_incident("Is the data fresh for the 2023-10-25 anomaly?")
        reply = result["reply"]
        
        assert "FRESH" in reply or "fresh" in reply.lower()
