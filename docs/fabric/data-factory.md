# Fabric Data Factory Pipelines

## Pipeline Design

1. **Ingest (Source -> Bronze)**
   - Copy Activity fetches raw JSON/CSV from simulated external systems.
   - Saves to Bronze Lakehouse folder as raw files.

2. **Bronze -> Silver (Clean & Type)**
   - Spark Notebook validates schemas.
   - Writes to Silver Lakehouse as Delta Tables.
   - Appends _run_id and _ingest_ts.

3. **Silver -> Gold (Aggregations)**
   - Spark Notebook performs business logic (e.g., aggregating orders into daily_revenue).
   - UPSERTs into Gold Lakehouse Delta Tables.

4. **Quality Checks**
   - Runs expectations on Silver/Gold tables.
   - Writes failures to data_quality_results.

5. **Anomaly Detection**
   - Reads Gold metrics and applies Z-score or Prophet forecasting.
   - Writes to nomalies.

## Failure Scenarios & Resolution

| Scenario | Detection | Alert | Incident | AI Investigation |
|----------|-----------|-------|----------|------------------|
| Schema Drift | Bronze->Silver job fails | Teams/Email Alert | Created | Agent extracts schema diff |
| Stale Pipeline | pipeline_runs freshness > 2h | SLA Alert | Created | Agent checks Data Factory logs |
| Missing Partition | Data Quality check fails | Warning | Created | Agent queries _run_id for gap |
| Duplicate Events | Eventhouse KQL check | Warning | Ignored | Agent flags during RCA |
| Late Event | Eventstream timestamp > ingest_ts | Metric Drop | Created | Agent correlates with latency metrics |
| Failed Gold Trans. | Silver->Gold job fails | SLA Alert | Created | Agent checks Spark logs |
| Eventstream Interruption| Eventhouse ingest rate = 0 | Critical Alert | Created | Agent analyzes platform health |
