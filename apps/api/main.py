from fastapi import FastAPI, HTTPException
import duckdb
from pydantic import BaseModel
from contextlib import asynccontextmanager
import math
import os

from apps.api.data_provider import get_data_provider

def replace_nan(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(v) for v in obj]
    return obj

DB_PATH = "data/datasentinel.db"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DuckDB views for local mode
    if os.environ.get("EXECUTION_MODE", "local").lower() == "local":
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
            
    # Validate agent availability
    from agents.orchestrator import check_llm_availability
    check_llm_availability()
    yield

app = FastAPI(title="DataSentinel API", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider = get_data_provider()

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "mode": os.environ.get("EXECUTION_MODE", "local").lower()}

@app.get("/pipelines")
def get_pipelines():
    return replace_nan(provider.get_pipeline_runs(10))

@app.get("/quality/latest")
def get_quality_latest():
    try:
        return replace_nan(provider.get_quality_latest())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies")
def get_anomalies():
    try:
        return replace_nan(provider.get_anomalies())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from agents.orchestrator import get_llm, investigate_incident

@app.post("/agent/chat")
def agent_chat(request: QueryRequest):
    try:
        result = investigate_incident(request.query)
        if "Error:" in result["reply"]:
            raise HTTPException(status_code=500, detail=result["reply"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Agent Error: {str(e)}")

@app.post("/agent/investigate")
def agent_investigate(incident_id: str, query: str):
    try:
        result = investigate_incident(query)
        if "Error:" in result["reply"]:
            raise HTTPException(status_code=500, detail=result["reply"])
        return {"incident_id": incident_id, "summary": result["reply"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/platform-summary")
def get_platform_summary():
    try:
        revenue_data = replace_nan(provider.get_revenue_trend())
        pipeline_runs = replace_nan(provider.get_pipeline_runs())
        
        return {
            "reliability_score": 94.5,
            "pipeline_freshness": "2h delayed",
            "revenue_trend": revenue_data,
            "pipeline_runs": pipeline_runs
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/lineage")
def get_lineage():
    try:
        return replace_nan(provider.get_lineage())
    except Exception as e:
        return {"error": str(e)}

@app.get("/metrics")
def get_metrics():
    try:
        return replace_nan(provider.get_metrics())
    except Exception as e:
        return {"error": str(e)}
