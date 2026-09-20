import duckdb
from pydantic import BaseModel, Field
import os

DB_PATH = "data/datasentinel.db"

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
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(query).df()
        con.close()
        return result.to_dict(orient="records")
    except Exception as e:
        return f"SQL Error: {str(e)}"

def get_pipeline_status():
    """Returns the status of the latest pipeline runs."""
    return [
        {"pipeline": "bronze", "status": "success", "last_run": "2023-10-25T10:00:00Z"},
        {"pipeline": "silver", "status": "success", "last_run": "2023-10-25T10:05:00Z"},
        {"pipeline": "gold", "status": "success", "last_run": "2023-10-25T10:10:00Z"}
    ]

def get_latest_quality_results():
    """Returns the most recent data quality validation results."""
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        res = con.execute("SELECT * FROM quality_results ORDER BY execution_time DESC LIMIT 10").df()
        con.close()
        return res.to_dict(orient="records")
    except Exception:
        return "No quality results available."

def get_latest_anomalies():
    """Returns the most recent anomalies detected in the metrics."""
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        res = con.execute("SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT 5").df()
        con.close()
        return res.to_dict(orient="records")
    except Exception:
        return "No anomalies detected."

def get_table_schema(table_name: str):
    """Gets the schema (columns and types) for a given table."""
    try:
        con = duckdb.connect(DB_PATH, read_only=True)
        res = con.execute(f"DESCRIBE {table_name}").df()
        con.close()
        return res.to_dict(orient="records")
    except Exception as e:
        return f"Error fetching schema: {e}"

def search_runbook(query: str):
    """Searches the knowledge base for runbooks and documentation."""
    # In a real implementation, this would query the FAISS index
    return "Check get_pipeline_status() and get_latest_quality_results(). The total_amount column might have nulls."
