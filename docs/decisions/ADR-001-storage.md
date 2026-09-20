# ADR-001: Storage Architecture

## Status
Accepted

## Context
We need a lightweight, cost-effective storage architecture for a free-tier compatible platform.

## Decision
We will use local file system with Parquet format for Bronze/Silver/Gold layers during local development. For Azure, we will use Azure Data Lake Storage Gen2 (Blob Storage).
DuckDB will be used to query Gold layer Parquet files directly.

## Consequences
- Zero database cost for raw/processed data storage.
- High performance for analytics queries.
- Requires robust directory management.
