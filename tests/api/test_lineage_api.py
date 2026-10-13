import math
import os
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

# Ensure test Fabric env vars are present for import
os.environ["FABRIC_SERVER"] = "test.server.fabric.microsoft.com"
os.environ["FABRIC_DATABASE"] = "test_lakehouse"
os.environ["FABRIC_TENANT_ID"] = "test-tenant-id"
os.environ["FABRIC_WORKSPACE_ID"] = "test-workspace-id"
os.environ["FABRIC_EVENTHOUSE_ID"] = "test-eventhouse-id"
os.environ["FABRIC_PIPELINE_ID"] = "test-pipeline-id"
os.environ["FABRIC_KQL_DATABASE"] = "test_kql_db"

from apps.api.main import app

client = TestClient(app)


def test_lineage_local_mode_success():
    with patch.dict(os.environ, {"EXECUTION_MODE": "local"}):
        response = client.get("/lineage")
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        assert len(data["nodes"]) > 0
        assert len(data["edges"]) > 0

        layers = {n["layer"] for n in data["nodes"]}
        expected_layers = {"Source", "Bronze", "Silver", "Gold", "Real-time", "Serving"}
        assert expected_layers.issubset(layers)


def test_lineage_fabric_mode_with_mocked_sql():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1234]
    mock_conn.cursor.return_value = mock_cursor

    with patch.dict(os.environ, {"EXECUTION_MODE": "fabric"}):
        with patch("apps.api.data_provider.FabricProvider._connection", return_value=mock_conn):
            response = client.get("/lineage")
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data

            table_nodes = [n for n in data["nodes"] if n["entity"] == "table"]
            assert len(table_nodes) > 0
            # All tables should have rows=1234 and status="active"
            for n in table_nodes:
                assert n["rows"] == 1234
                assert n["status"] == "active"


def test_lineage_fabric_mode_sql_failure_fallback():
    """When Fabric SQL endpoint fails or times out, logical pipeline metadata is preserved with rows=None and status='unknown' without claiming false verification."""
    with patch.dict(os.environ, {"EXECUTION_MODE": "fabric"}):
        with patch("apps.api.data_provider.FabricProvider._connection", side_effect=Exception("Timeout connecting to Fabric Lakehouse")):
            response = client.get("/lineage")
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data
            assert len(data["nodes"]) > 0

            table_nodes = [n for n in data["nodes"] if n["entity"] == "table"]
            for n in table_nodes:
                assert n["rows"] is None
                assert n["status"] == "unknown"


def test_lineage_empty_valid_metadata():
    with patch("apps.api.data_provider.LocalDuckDBProvider.get_lineage", return_value={"nodes": [], "edges": []}):
        with patch.dict(os.environ, {"EXECUTION_MODE": "local"}):
            response = client.get("/lineage")
            assert response.status_code == 200
            data = response.json()
            assert data == {"nodes": [], "edges": []}


def test_lineage_provider_failure_returns_500():
    with patch("apps.api.data_provider.LocalDuckDBProvider.get_lineage", side_effect=RuntimeError("Underlying engine failure")):
        with patch.dict(os.environ, {"EXECUTION_MODE": "local"}):
            response = client.get("/lineage")
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert data["detail"] == "Failed to retrieve lineage data"
            assert "error" not in data or data.get("detail")


def test_lineage_malformed_provider_output_returns_502():
    with patch("apps.api.data_provider.LocalDuckDBProvider.get_lineage", return_value={"wrong_shape": True}):
        with patch.dict(os.environ, {"EXECUTION_MODE": "local"}):
            response = client.get("/lineage")
            assert response.status_code == 502
            data = response.json()
            assert data["detail"] == "Invalid lineage data received from data provider"


def test_lineage_nan_safe_replacement():
    mock_data = {
        "nodes": [
            {"id": "node_1", "name": "Node 1", "layer": "Bronze", "status": "active", "entity": "table", "rows": float("nan")}
        ],
        "edges": []
    }
    with patch("apps.api.data_provider.LocalDuckDBProvider.get_lineage", return_value=mock_data):
        with patch.dict(os.environ, {"EXECUTION_MODE": "local"}):
            response = client.get("/lineage")
            assert response.status_code == 200
            data = response.json()
            assert data["nodes"][0]["rows"] is None
