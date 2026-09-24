# DataSentinel Lakehouse (Medallion Architecture)

## Medallion Layers

- **Bronze**: Raw data ingested from sources.
- **Silver**: Cleaned, filtered, deduplicated, and typed data.
- **Gold**: Business-level aggregates ready for the API.

## Delta-Table Expectations

All Delta tables must enforce:
1. **Primary Keys**: Used for MERGE/UPSERT operations (e.g., order_id).
2. **Partitioning**: Partition large tables (e.g., orders, vents) by date or year_month.
3. **Ingestion Timestamp**: _ingest_ts to track data arrival.
4. **Batch ID / Pipeline Run ID**: _run_id for lineage mapping.
5. **Schema Versioning**: Utilizing Delta Lake schema evolution controls.

## Table Schemas

### Silver Layer
- customers (customer_id, email, segment, created_at, _run_id)
- products (product_id, name, category, price, _run_id)
- orders (order_id, customer_id, order_date, status, total_amount, _run_id)
- order_items (item_id, order_id, product_id, quantity, unit_price, _run_id)
- payments (payment_id, order_id, amount, payment_method, status, _run_id)
- inventory (product_id, warehouse, stock_level, updated_at, _run_id)

### Gold Layer
- daily_revenue (date, total_revenue, total_orders, _run_id)
- pipeline_runs (run_id, pipeline_name, start_time, duration_sec, records, status)
- data_quality_results (rule_id, dataset_name, rule_name, status, failed_rows, execution_time)
- nomalies (anomaly_id, timestamp, metric, value, baseline_value, severity)
- incidents (incident_id, title, status, created_at, resolved_at)
