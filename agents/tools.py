from pydantic import BaseModel, Field
import os
import sys

# Ensure apps module is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from apps.api.data_provider import get_data_provider

class SqlToolSchema(BaseModel):
    query: str = Field(..., description="The SELECT query to execute against the analytics database.")

def run_readonly_sql(query: str):
    """Executes a read-only SQL query against the analytics database."""
    query_upper = query.upper()
    forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE"]
    
    for kw in forbidden_keywords:
        if kw in query_upper:
            return f"Error: {kw} is not allowed. Only SELECT queries are permitted."
            
    try:
        provider = get_data_provider()
        return provider._execute(query)
    except Exception as e:
        return f"SQL Error: {str(e)}"

def get_pipeline_status():
    """Returns the status of the latest pipeline runs. Useful to check what failed and why."""
    try:
        provider = get_data_provider()
        return provider.get_pipeline_runs(limit=10)
    except Exception as e:
        return f"Error: {str(e)}"

def get_latest_quality_results():
    """Returns the most recent data quality validation results. Useful to check data quality status."""
    try:
        provider = get_data_provider()
        return provider.get_quality_latest(limit=20)
    except Exception as e:
        return f"Error: {str(e)}"

def get_latest_anomalies():
    """Returns the most recent anomalies detected in the real-time event streams."""
    try:
        provider = get_data_provider()
        return provider.get_anomalies(limit=10)
    except Exception as e:
        return f"Error: {str(e)}"

def get_revenue_and_metrics():
    """Returns the recent revenue trend and KPIs (total orders, unique customers, etc)."""
    try:
        provider = get_data_provider()
        return provider.get_metrics(limit=30)
    except Exception as e:
        return f"Error: {str(e)}"

def get_platform_summary():
    """Returns the overall platform reliability and freshness."""
    try:
        provider = get_data_provider()
        return provider.get_platform_summary()
    except Exception as e:
        return f"Error: {str(e)}"
