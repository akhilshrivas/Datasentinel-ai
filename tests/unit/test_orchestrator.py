import os
import pytest
from unittest.mock import patch, MagicMock
from agents.orchestrator import get_llm, create_agent, check_llm_availability
from agents.tools import run_readonly_sql

def test_model_initialization_ollama():
    with patch.dict(os.environ, {"AI_PROVIDER": "ollama", "OLLAMA_API_URL": "http://fake:11434/v1"}):
        llm = get_llm()
        assert llm.model == "qwen3:4b"
        # The base URL configuration is private in ChatOpenAI depending on version, 
        # but we can check the provider logic succeeded.

def test_model_initialization_azure():
    with patch.dict(os.environ, {
        "AI_PROVIDER": "azure", 
        "AZURE_OPENAI_ENDPOINT": "https://fake.azure.com",
        "AZURE_OPENAI_API_KEY": "fake_key"
    }):
        llm = get_llm()
        # Verify it instantiated ChatOpenAI with azure configs
        assert hasattr(llm, "azure_endpoint") or getattr(llm, "deployment_name", None) == "gpt-4"

def test_agent_creation():
    llm = MagicMock()
    agent = create_agent(llm)
    assert agent is not None
    # Agent should have our tools mapped
    
def test_provider_configuration_validation_success():
    with patch.dict(os.environ, {"AI_PROVIDER": "ollama", "OLLAMA_API_URL": "http://localhost:11434/v1"}):
        with patch("httpx.get") as mock_get:
            mock_get.return_value.status_code = 200
            check_llm_availability()
            mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=3.0)

def test_provider_configuration_validation_failure():
    with patch.dict(os.environ, {"AI_PROVIDER": "ollama", "OLLAMA_API_URL": "http://localhost:11434/v1"}):
        with patch("httpx.get") as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            with pytest.raises(RuntimeError, match="Ollama provider is configured but unavailable"):
                check_llm_availability()

@pytest.mark.parametrize("query", [
    "DROP TABLE orders;",
    "DELETE FROM users WHERE id=1;",
    "UPDATE inventory SET stock=0;",
    "INSERT INTO anomalies (id) VALUES (1);",
    "ALTER TABLE customers ADD COLUMN age INT;",
    "TRUNCATE TABLE daily_revenue;"
])
def test_sql_safety_layer(query):
    result = run_readonly_sql(query)
    assert "is not allowed. Only SELECT queries are permitted" in result
