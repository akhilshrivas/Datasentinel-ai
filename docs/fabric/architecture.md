# Microsoft Fabric Architecture

DataSentinel AI provides a dual execution architecture, supporting both a completely local environment and a cloud-native Microsoft Fabric environment.

## Execution Modes

1. **Local Mode (EXECUTION_MODE=local)**: Uses Polars, DuckDB, Parquet, and a local LangGraph/Ollama agent.
2. **Fabric Mode (EXECUTION_MODE=fabric)**: Uses Microsoft Fabric OneLake, Eventstream, Eventhouse, and Data Factory.

## Cloud Architecture

### Batch Pipeline (Data Factory)
`mermaid
graph LR
  subgraph External
    Source[REST API / DBs]
  end
  subgraph Fabric Data Factory
    CopyData[Copy Activity]
    Notebooks[Spark Notebooks]
  end
  subgraph OneLake (DataSentinel Lakehouse)
    Bronze[Bronze: Raw]
    Silver[Silver: Cleaned]
    Gold[Gold: Aggregates]
  end
  Source --> CopyData
  CopyData --> Bronze
  Bronze --> Notebooks
  Notebooks --> Silver
  Notebooks --> Gold
`

### Streaming Pipeline (Real-Time Intelligence)
`mermaid
graph LR
  subgraph Producer
    Simulator[Event Simulator]
  end
  subgraph Fabric Real-Time
    Eventstream[Eventstream]
    Eventhouse[Eventhouse (KQL)]
  end
  subgraph Application
    Detector[Anomaly Detector]
    Incidents[Incident Table]
  end
  Simulator --> Eventstream
  Eventstream --> Eventhouse
  Eventhouse --> Detector
  Detector --> Incidents
`

### Application & AI Layer
`mermaid
graph TD
  subgraph Fabric
    Gold[Gold Lakehouse]
    Eventhouse[Eventhouse]
  end
  subgraph Backend
    FastAPI[FastAPI]
    Agent[LangGraph Agent]
  end
  subgraph Frontend
    React[React Ops Console]
  end
  
  Gold --> FastAPI
  Eventhouse --> FastAPI
  FastAPI --> React
  React --> FastAPI
  FastAPI --> Agent
  Agent --> FastAPI
`

## Local/Cloud Boundary

The abstraction boundary exists in pps/api/data_provider.py. The DataProvider interface ensures that the FastAPI application and the LangGraph agent never hardcode SQL syntax specific to DuckDB or Fabric.

When EXECUTION_MODE=fabric, the application communicates via Semantic Link or the SQL Analytics Endpoint, abstracting away the underlying OneLake Delta tables.
