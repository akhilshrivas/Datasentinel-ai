# Local vs Cloud Architecture

## Why Both?

DataSentinel provides a **Local Mode** to ensure the project remains accessible, testable, and free for individual developers without requiring Azure credentials or paid cloud resources.

The **Fabric Mode** provides an enterprise-ready reference architecture proving that the exact same Agentic AI workflows operate at petabyte scale.

## The Boundary

The system cleanly separates the data tier from the application tier:

- **Local**: DuckDB reading local .parquet files.
- **Cloud**: FastAPI queries OneLake SQL Analytics Endpoints and Eventhouse KQL.

The boundary is enforced by pps/api/data_provider.py implementing DataProvider. The LangGraph agent does not know whether it is interacting with DuckDB or Microsoft Fabric—it only receives structured data from the provider.
