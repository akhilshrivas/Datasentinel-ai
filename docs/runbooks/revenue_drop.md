# Runbook: Revenue Drop Incident

## Description
This runbook provides steps to troubleshoot when the daily revenue metric drops significantly.

## Possible Causes
1. **Pipeline Failure**: The Bronze or Silver pipeline failed to process recent data.
2. **Data Quality Issue**: High number of nulls in `total_amount` or rejected records in Silver layer.
3. **Late-Arriving Data**: Upstream system delay.
4. **Schema Drift**: The `total_amount` column was renamed or type changed in the source data.

## Remediation Steps
1. Check `get_pipeline_status()` to ensure the pipelines ran successfully.
2. Check `get_latest_quality_results()` for any FAIL statuses on the `orders` dataset.
3. Check `get_table_schema('orders')` to ensure `total_amount` exists and is numeric.
4. If it's a quality issue, examine the failed records and quarantine them.
