# DataPulse AI

DataPulse AI (formerly DataSentinel) is an intelligent data-platform operations console powered by Agentic AI. It provides a centralized dashboard and AI-driven investigation tool to monitor data pipelines, track anomalies, measure data quality, and visualize data lineage across enterprise architectures.

## 🚀 Key Features
- **AI-Powered Investigations**: Ask natural language questions (e.g., "What happened in the latest pipeline run?") and get deterministic, actionable answers.
- **Data Lineage Graph**: Interactive visualization of data flowing from Source → Bronze → Silver → Gold layers, including real-time event streams.
- **Real-Time Anomaly Detection**: Monitor event streams and identify detected anomalies instantly.
- **Data Quality Gates**: Track table-level data quality constraints (PK violations, nulls, duplicates) in real-time.

## 🛠️ Tech Stack
### Frontend
- **React 19** & **Vite**: Ultra-fast UI rendering.
- **Lucide-React** & **Recharts**: Modern iconography and interactive telemetry charts.
- **Custom CSS**: Lightweight, utility-free modular styling with native CSS variables.

### Backend & AI
- **FastAPI** (Python): High-performance REST API.
- **LangChain & LangGraph**: AI agent orchestration with strict deterministic routing for operational queries.
- **Local AI / LLMs**: Seamless support for local models (via Ollama) or cloud providers (Azure OpenAI).

### Data Layer
- **Microsoft Fabric (Production)**: Native integration with Fabric Lakehouse (Delta), Eventstream, Eventhouse (KQL), and Data Factory via PyODBC and Azure Entra ID.
- **DuckDB (Local Dev)**: Fallback local execution mode using Polars and Parquet files for offline zero-cost development.

## ⚙️ Quick Start

### 1. Environment Setup
Configure your environment variables. Ensure no secrets are hardcoded.
```bash
# Frontend
cp apps/web/.env.example apps/web/.env

# Backend
# Configure EXECUTION_MODE=fabric or local in your backend environment.
```

### 2. Backend (FastAPI)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # (or venv\\Scripts\\activate on Windows)

# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

### 3. Frontend (React/Vite)
```bash
cd apps/web
npm install
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

## 🔒 Security & Safe AI
- **Zero Secrets Committed**: All credentials (Tokens, Azure Entra IDs, API Keys) are strictly injected via `.env`.
- **Sanitized AI Outputs**: The backend aggressively strips `<think>` tokens and reasoning logic before resolving data to the UI, ensuring clean, production-safe responses.
