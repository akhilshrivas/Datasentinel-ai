# DataSentinel AI - Project Status

## Implemented Features
- [x] Phase 1: Repository architecture and base configuration (Makefile, Docker, etc.)
- [x] Phase 2: Synthetic Data Generation (`customers`, `products`, `orders`, etc.)
- [x] Phase 3: Bronze/Silver/Gold Pipeline using Polars
- [x] Phase 4: Data Contracts (`orders.yaml`) and Data Quality Engine
- [x] Phase 5: Anomaly Detection (Statistical Z-score on Daily Revenue)
- [x] Phase 6: SQL Analytics API (FastAPI + DuckDB)
- [x] Phase 7: RAG Knowledge Indexer (FAISS + Langchain)
- [x] Phase 8: AI Agent Tools (Pipeline status, Quality, Anomalies, Read-only SQL)
- [x] Phase 9: AI Agent Orchestration (ReAct architecture)
- [x] Phase 10: React Frontend Setup (Vite scaffolding)
- [x] Phase 11: Observability / Failure Injection Scripts
- [x] Phase 13: Terraform Definitions (Azure Storage, Container Apps)
- [x] Phase 14: GitHub Actions CI/CD Pipeline
- [x] Phase 15: Full End-to-End Demo Script (`demo.py`)

## Tested Features
- Python tool execution flows created. E2E test runs successfully upon `pip install` completion.

## Azure Resources
- Storage Account (Standard LRS)
- Log Analytics Workspace (Free Tier)
- Container Apps Environment (Serverless)
- *All configured within Free Tier / Azure for Students limits*

## Free-Tier Assumptions
- No VM/AKS deployment
- Uses local Parquet instead of paid DB for raw storage
- Uses DuckDB for API serving without DB limits
- Azure ML / Synapse are avoided entirely. 
- Container Apps is utilized under free grants.

## Known Limitations
- Data schema drift tests are basic and check for missing columns.
- Anomaly detection uses simple Z-score, but extensible.
- AI Agent requires LLM Provider credentials to execute tool calls completely.

## Commands to Run
1. `make setup` - Installs Python dependencies
2. `make demo` - Runs the complete synthetic data → Bronze/Silver/Gold → Quality checks → Anomaly Detection → Failure Injection loop.
3. `make api` - Starts the FastAPI server querying the DuckDB backend
4. `make frontend` - Starts the React dashboard.

## Demo Scenario
The `demo.py` script orchestrates data creation, pipeline runs, validates data quality, detects baseline anomalies, and intentionally injects a revenue drop failure. The API exposes this for the Agent to investigate using its tools.

## Future Enhancements
- Switch from local FAISS to Azure AI Search Free Tier for remote document retrieval.
- Deploy Postgres / Azure SQL Serverless to augment DuckDB.
- Connect real-time streaming endpoint to the frontend dashboard.
