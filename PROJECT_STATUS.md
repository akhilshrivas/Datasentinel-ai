# DataPulse AI - Project Status

## Implemented Features
- [x] Phase 1: Repository architecture and base configuration (Makefile, Docker, etc.)
- [x] Phase 2: Synthetic Data Generation (`customers`, `products`, `orders`, etc.)
- [x] Phase 3: Bronze/Silver/Gold Pipeline using Microsoft Fabric Lakehouse (Delta)
- [x] Phase 4: Data Contracts (`orders.yaml`) and Data Quality Engine
- [x] Phase 5: Anomaly Detection (Statistical Z-score & Real-time KQL Eventhouse)
- [x] Phase 6: SQL Analytics API (FastAPI + Fabric PyODBC)
- [x] Phase 7: RAG Knowledge Indexer (FAISS + Langchain)
- [x] Phase 8: AI Agent Tools (Pipeline status, Quality, Anomalies, Business Metrics)
- [x] Phase 9: AI Agent Orchestration (LangGraph + Deterministic Tool Routing)
- [x] Phase 10: React Data Lineage & Operations Console
- [x] Phase 11: Real-Time Eventstream simulator (`event_simulator.py`)
- [x] Phase 12: Azure Infrastructure Provisioning Definitions (Terraform)
- [x] Phase 13: GitHub Actions CI/CD Pipeline

## Core Architecture
- **Data Engine**: Microsoft Fabric Lakehouse (Delta Tables), Eventstream, Eventhouse (KQL), Azure Data Factory.
- **Serving Layer**: FastAPI querying Lakehouse natively via PyODBC & Entra ID.
- **Frontend Layer**: React 19 + Vite dashboard resolving 28 nodes and 35 edges in deterministic lineage.
- **AI Agent**: LangGraph operational assistant with strict zero-leakage reasoning, safely rendering deterministic charts and JSON telemetry.

## Commands to Run
1. `pip install -r requirements.txt` - Installs Python dependencies
2. `npm run dev` (in `apps/web`) - Starts the React dashboard
3. `uvicorn apps.api.main:app` - Starts the FastAPI server

## Known Limitations
- Data schema drift tests are basic and check for missing columns.
- AI Agent requires LLM Provider credentials to execute advanced conversational fallback flows.

## Completed Enhancements
- Migrated from local Parquet/DuckDB to Enterprise Microsoft Fabric Cloud.
- Connected real-time streaming endpoints directly to the frontend Anomalies dashboard.
- Secured AI responses strictly replacing hallucinatory reasoning blocks with deterministic tools.
