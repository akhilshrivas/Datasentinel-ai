import os
from fastapi import FastAPI, HTTPException
import duckdb
from pydantic import BaseModel
from contextlib import asynccontextmanager

# DuckDB setup
DB_PATH = "data/datasentinel.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DuckDB and create views over Parquet files
    con = duckdb.connect(DB_PATH)
    try:
        if os.path.exists("data/gold/daily_revenue.parquet"):
            con.execute("CREATE OR REPLACE VIEW daily_revenue AS SELECT * FROM read_parquet('data/gold/daily_revenue.parquet')")
        if os.path.exists("data/gold/product_metrics.parquet"):
            con.execute("CREATE OR REPLACE VIEW product_metrics AS SELECT * FROM read_parquet('data/gold/product_metrics.parquet')")
        if os.path.exists("data/gold/anomalies.parquet"):
            con.execute("CREATE OR REPLACE VIEW anomalies AS SELECT * FROM read_parquet('data/gold/anomalies.parquet')")
        if os.path.exists("data/gold/quality_results.parquet"):
            con.execute("CREATE OR REPLACE VIEW quality_results AS SELECT * FROM read_parquet('data/gold/quality_results.parquet')")
    except Exception as e:
        print(f"Error initializing DB views: {e}")
    finally:
        con.close()
    yield

app = FastAPI(title="DataSentinel API", lifespan=lifespan)

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/pipelines")
def get_pipelines():
    return {"status": "ok", "pipelines": ["bronze", "silver", "gold"]}

@app.get("/quality/latest")
def get_quality_latest():
    try:
        con = duckdb.connect(DB_PATH)
        res = con.execute("SELECT * FROM quality_results ORDER BY execution_time DESC LIMIT 100").fetchall()
        cols = [desc[0] for desc in con.description]
        con.close()
        return [dict(zip(cols, row)) for row in res]
    except Exception as e:
        return {"error": str(e)}

@app.get("/anomalies")
def get_anomalies():
    try:
        con = duckdb.connect(DB_PATH)
        res = con.execute("SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT 50").fetchall()
        cols = [desc[0] for desc in con.description]
        con.close()
        return [dict(zip(cols, row)) for row in res]
    except Exception as e:
        return {"error": str(e)}

from agents.orchestrator import create_agent

@app.post("/agent/chat")
def agent_chat(request: QueryRequest):
    try:
        agent = create_agent()
        response = agent.run(request.query)
        return {"reply": response, "tool_calls": []}
    except Exception as e:
        return {"reply": f"Error: {str(e)}", "tool_calls": []}

@app.post("/agent/investigate")
def agent_investigate(incident_id: str, query: str):
    from agents.orchestrator import investigate_incident
    try:
        response = investigate_incident(query)
        return {"incident_id": incident_id, "summary": response}
    except Exception as e:
        return {"error": str(e)}
