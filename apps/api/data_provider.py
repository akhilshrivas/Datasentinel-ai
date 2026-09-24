import os
import struct
from typing import List, Dict, Any

import duckdb
import pyodbc
import requests
from azure.identity import AzureCliCredential


EXECUTION_MODE = os.environ.get("EXECUTION_MODE", "local").lower()

FABRIC_SERVER = os.environ.get(
    "FABRIC_SERVER",
    "nzjdbrqs77kupaq2ajaj4plolu-5z3a2bhrwrvu7fp3emdned4oo4.datawarehouse.fabric.microsoft.com",
)

FABRIC_DATABASE = os.environ.get(
    "FABRIC_DATABASE",
    "DataSentinel_Lakehouse",
)

FABRIC_TENANT_ID = os.environ.get(
    "FABRIC_TENANT_ID",
    "c630526e-ff12-47d5-821a-02409e3d6e5d",
)

FABRIC_WORKSPACE_ID = "040d76ee-b4f1-4f6b-95fb-2306d20f8e77"
FABRIC_EVENTHOUSE_ID = "9a8e0481-fdd4-4c66-8dee-9e99f0dfdd67"
FABRIC_KQL_DATABASE = "DataSentinel_Eventhouse"


class DataProvider:
    def get_revenue_trend(self, limit: int = 7) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_pipeline_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_quality_latest(self, limit: int = 100) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        raise NotImplementedError


    def get_lineage(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_metrics(self, limit: int = 30) -> List[Dict[str, Any]]:
        raise NotImplementedError


class LocalDuckDBProvider(DataProvider):
    def __init__(self, db_path: str = "data/datasentinel.db"):
        self.db_path = db_path

    def _execute(self, query: str) -> List[Dict[str, Any]]:
        try:
            con = duckdb.connect(self.db_path)
            res = con.execute(query).fetchall()
            cols = [desc[0] for desc in con.description]
            con.close()
            return [dict(zip(cols, row)) for row in res]
        except Exception as e:
            print(f"DuckDB Query Error: {e}")
            return []

    def get_revenue_trend(self, limit: int = 7) -> List[Dict[str, Any]]:
        return self._execute(
            f"""
            SELECT *
            FROM daily_revenue
            ORDER BY date DESC
            LIMIT {limit}
            """
        )

    def get_pipeline_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            {
                "id": "bronze_ingest",
                "status": "success",
                "duration_sec": 45,
                "records": 150000,
                "timestamp": "2026-09-21T10:00:00Z",
            },
            {
                "id": "silver_clean",
                "status": "success",
                "duration_sec": 120,
                "records": 149500,
                "timestamp": "2026-09-21T10:05:00Z",
            },
            {
                "id": "gold_metrics",
                "status": "failed",
                "duration_sec": 15,
                "records": 0,
                "timestamp": "2026-09-21T10:10:00Z",
            },
        ][:limit]

    def get_quality_latest(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._execute(
            f"""
            SELECT *
            FROM quality_results
            ORDER BY execution_time DESC
            LIMIT {limit}
            """
        )

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._execute(
            f"""
            SELECT *
            FROM anomalies
            ORDER BY timestamp DESC
            LIMIT {limit}
            """
        )


    def get_lineage(self) -> Dict[str, Any]:
        raise NotImplementedError

    def get_metrics(self, limit: int = 30) -> List[Dict[str, Any]]:
        return self._execute(
            f"""
            SELECT *
            FROM product_metrics
            ORDER BY date DESC
            LIMIT {limit}
            """
        )


class FabricProvider(DataProvider):
    """
    Fabric implementation using the Lakehouse SQL analytics endpoint.

    Local development authentication:
    Azure CLI -> AzureCliCredential -> Entra access token -> pyodbc
    """

    SQL_COPT_SS_ACCESS_TOKEN = 1256

    def __init__(self):
        self.credential = AzureCliCredential(
            tenant_id=FABRIC_TENANT_ID
        )

    def _connection(self):
        token = self.credential.get_token(
            "https://database.windows.net/.default"
        ).token

        token_bytes = token.encode("utf-16-le")
        access_token = struct.pack(
            f"<I{len(token_bytes)}s",
            len(token_bytes),
            token_bytes,
        )

        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={FABRIC_SERVER};"
            f"DATABASE={FABRIC_DATABASE};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
        )

        return pyodbc.connect(
            connection_string,
            attrs_before={
                self.SQL_COPT_SS_ACCESS_TOKEN: access_token
            },
            timeout=30,
        )

    def _execute(
        self,
        query: str,
        params: tuple = (),
    ) -> List[Dict[str, Any]]:
        conn = None

        try:
            conn = self._connection()
            conn.timeout = 15
            cursor = conn.cursor()
            cursor.execute(query, params)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

        except Exception as e:
            print(f"Fabric SQL Error: {e}")
            return []
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def get_revenue_trend(self, limit: int = 7) -> List[Dict[str, Any]]:
        return self._execute(
            f"""
            SELECT
                order_date AS date,
                order_count,
                daily_revenue,
                average_order_value
            FROM dbo.daily_revenue
            ORDER BY order_date DESC
            OFFSET 0 ROWS
            FETCH NEXT {limit} ROWS ONLY
            """
        )

    def get_pipeline_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            token = self.credential.get_token(
                "https://api.fabric.microsoft.com/.default"
            ).token

            headers = {
                "Authorization": f"Bearer {token}"
            }

            url = (
                "https://api.fabric.microsoft.com/v1/"
                "workspaces/040d76ee-b4f1-4f6b-95fb-2306d20f8e77/"
                "items/9544e045-6914-49b8-92ca-56cb8cd64185/"
                "jobs/instances?jobType=Pipeline"
            )

            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            jobs = response.json().get("value", [])

            results = []

            for job in jobs[:limit]:
                results.append({
                    "id": job.get("id"),
                    "item_id": job.get("itemId"),
                    "job_type": job.get("jobType"),
                    "invoke_type": job.get("invokeType"),
                    "status": job.get("status"),
                    "start_time": job.get("startTimeUtc"),
                    "failure_reason": job.get("failureReason"),
                })

            return results

        except Exception as e:
            print(f"Fabric Pipeline API Error: {e}")
            return []

    def get_quality_latest(self, limit: int = 100) -> List[Dict[str, Any]]:
        query = """
        SELECT 'silver_customers' as table_name, 'customer_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(customer_id) as null_keys, COUNT(*) - COUNT(DISTINCT customer_id) as duplicate_keys FROM silver_customers
        UNION ALL
        SELECT 'silver_products' as table_name, 'product_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(product_id) as null_keys, COUNT(*) - COUNT(DISTINCT product_id) as duplicate_keys FROM silver_products
        UNION ALL
        SELECT 'silver_orders' as table_name, 'order_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(order_id) as null_keys, COUNT(*) - COUNT(DISTINCT order_id) as duplicate_keys FROM silver_orders
        UNION ALL
        SELECT 'silver_order_items' as table_name, 'order_id, product_id' as key_column, COUNT(*) as total_rows, SUM(CASE WHEN order_id IS NULL OR product_id IS NULL THEN 1 ELSE 0 END) as null_keys, COUNT(*) - (SELECT COUNT(*) FROM (SELECT DISTINCT order_id, product_id FROM silver_order_items) t) as duplicate_keys FROM silver_order_items
        UNION ALL
        SELECT 'silver_payments' as table_name, 'payment_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(payment_id) as null_keys, COUNT(*) - COUNT(DISTINCT payment_id) as duplicate_keys FROM silver_payments
        UNION ALL
        SELECT 'silver_inventory' as table_name, 'product_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(product_id) as null_keys, COUNT(*) - COUNT(DISTINCT product_id) as duplicate_keys FROM silver_inventory
        UNION ALL
        SELECT 'silver_events' as table_name, 'event_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(event_id) as null_keys, COUNT(*) - COUNT(DISTINCT event_id) as duplicate_keys FROM silver_events
        UNION ALL
        SELECT 'daily_revenue' as table_name, 'order_date' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(order_date) as null_keys, COUNT(*) - COUNT(DISTINCT order_date) as duplicate_keys FROM daily_revenue
        UNION ALL
        SELECT 'daily_orders' as table_name, 'order_date, status' as key_column, COUNT(*) as total_rows, SUM(CASE WHEN order_date IS NULL OR status IS NULL THEN 1 ELSE 0 END) as null_keys, COUNT(*) - (SELECT COUNT(*) FROM (SELECT DISTINCT order_date, status FROM daily_orders) t) as duplicate_keys FROM daily_orders
        UNION ALL
        SELECT 'customer_metrics' as table_name, 'customer_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(customer_id) as null_keys, COUNT(*) - COUNT(DISTINCT customer_id) as duplicate_keys FROM customer_metrics
        UNION ALL
        SELECT 'product_metrics' as table_name, 'product_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(product_id) as null_keys, COUNT(*) - COUNT(DISTINCT product_id) as duplicate_keys FROM product_metrics
        UNION ALL
        SELECT 'inventory_metrics' as table_name, 'product_id' as key_column, COUNT(*) as total_rows, COUNT(*) - COUNT(product_id) as null_keys, COUNT(*) - COUNT(DISTINCT product_id) as duplicate_keys FROM inventory_metrics
        """
        try:
            results = self._execute(query)
            from datetime import datetime, timezone
            now_str = datetime.now(timezone.utc).isoformat()
            
            output = []
            for row in results:
                failed = row['null_keys'] + row['duplicate_keys']
                status = 'failed' if failed > 0 else 'passed'
                
                output.append({
                    'dataset_name': row['table_name'],
                    'rule_name': f"PK_Constraint ({row['key_column']})",
                    'status': status,
                    'failed_rows': failed,
                    'total_rows': row['total_rows'],
                    'null_keys': row['null_keys'],
                    'duplicate_keys': row['duplicate_keys'],
                    'execution_time': now_str
                })
            return output
        except Exception as e:
            print(f"Fabric Quality Error: {e}")
            return []

    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            # Get Eventhouse query endpoint
            fabric_token = self.credential.get_token(
                "https://api.fabric.microsoft.com/.default"
            ).token

            fabric_headers = {
                "Authorization": f"Bearer {fabric_token}"
            }

            eventhouse_url = (
                f"https://api.fabric.microsoft.com/v1/workspaces/"
                f"{FABRIC_WORKSPACE_ID}/eventhouses/{FABRIC_EVENTHOUSE_ID}"
            )

            eventhouse_response = requests.get(
                eventhouse_url,
                headers=fabric_headers,
                timeout=30,
            )
            eventhouse_response.raise_for_status()

            query_service_uri = (
                eventhouse_response.json()
                .get("properties", {})
                .get("queryServiceUri")
            )

            if not query_service_uri:
                raise RuntimeError("Eventhouse queryServiceUri was not returned")

            # Token for Kusto/Eventhouse
            kusto_token = self.credential.get_token(
                "https://kusto.kusto.windows.net/.default"
            ).token

            kql = f"""
            realtime_events
            | extend event_time = todatetime(timestamp)
            | extend anomaly =
                case(
                    event_type == "order_cancelled", "ORDER_CANCELLED",
                    event_type == "payment_completed", "PAYMENT_COMPLETED",
                    event_type == "inventory_updated", "INVENTORY_UPDATED",
                    event_type == "customer_updated", "CUSTOMER_UPDATED",
                    event_type == "order_created", "ORDER_CREATED",
                    "OTHER"
                )
            | where event_type == "order_cancelled"
            | order by event_time desc
            | take {limit}
            """

            response = requests.post(
                f"{query_service_uri}/v1/rest/query",
                headers={
                    "Authorization": f"Bearer {kusto_token}",
                    "Content-Type": "application/json",
                },
                json={
                    "db": FABRIC_KQL_DATABASE,
                    "csl": kql,
                },
                timeout=30,
            )

            response.raise_for_status()

            payload = response.json()

            tables = payload.get("Tables", [])
            if not tables:
                return []

            rows = tables[0].get("Rows", [])
            columns = [
                col["ColumnName"]
                for col in tables[0].get("Columns", [])
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

        except Exception as e:
            print(f"Fabric Eventhouse Error: {e}")
            return []


    def get_lineage(self) -> Dict[str, Any]:
        try:
            tables = [
                'bronze_customers', 'bronze_products', 'bronze_orders', 'bronze_order_items', 'bronze_payments', 'bronze_events', 'bronze_inventory',
                'silver_customers', 'silver_products', 'silver_orders', 'silver_order_items', 'silver_payments', 'silver_events', 'silver_inventory',
                'daily_revenue', 'daily_orders', 'customer_metrics', 'product_metrics', 'inventory_metrics'
            ]
            
            counts = {}
            conn = None
            try:
                conn = self._connection()
                conn.timeout = 30
                cursor = conn.cursor()
                for t in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM dbo.{t}")
                        res = cursor.fetchone()
                        counts[t] = res[0] if res else None
                    except Exception as loop_e:
                        print(f"Failed to fetch count for {t}: {loop_e}")
                        counts[t] = None
            except Exception as e:
                print(f"Fabric Lineage Connection Error: {e}")
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                
            nodes = [
                {"id": "src_crm", "name": "CRM System", "layer": "Source", "status": "active", "entity": "source"},
                {"id": "src_ecommerce", "name": "E-Commerce Web", "layer": "Source", "status": "active", "entity": "source"},
                {"id": "src_inventory", "name": "Inventory App", "layer": "Source", "status": "active", "entity": "source"},
                {"id": "src_events", "name": "Event Simulator", "layer": "Source", "status": "active", "entity": "source"},
            ]
            
            for t in tables:
                if t.startswith('bronze_'):
                    layer = 'Bronze'
                elif t.startswith('silver_'):
                    layer = 'Silver'
                else:
                    layer = 'Gold'
                val = counts.get(t, None)
                nodes.append({
                    "id": t,
                    "name": t,
                    "layer": layer,
                    "status": "active" if val is not None else "unknown",
                    "entity": "table",
                    "rows": val
                })
                
            nodes.extend([
                {"id": "fabric_eventstream", "name": "Fabric Eventstream", "layer": "Real-time", "status": "active", "entity": "stream"},
                {"id": "fabric_eventhouse", "name": "Fabric Eventhouse", "layer": "Real-time", "status": "active", "entity": "kql_db"},
                {"id": "api_anomalies", "name": "Anomaly API", "layer": "Serving", "status": "active", "entity": "api"},
                {"id": "api_metrics", "name": "Metrics API", "layer": "Serving", "status": "active", "entity": "api"},
                {"id": "api_quality", "name": "Quality API", "layer": "Serving", "status": "active", "entity": "api"},
            ])
            
            edges = [
                {"source": "src_crm", "target": "bronze_customers"},
                {"source": "src_ecommerce", "target": "bronze_orders"},
                {"source": "src_ecommerce", "target": "bronze_order_items"},
                {"source": "src_ecommerce", "target": "bronze_payments"},
                {"source": "src_ecommerce", "target": "bronze_products"},
                {"source": "src_inventory", "target": "bronze_inventory"},
                {"source": "src_events", "target": "bronze_events"},
                
                {"source": "bronze_customers", "target": "silver_customers"},
                {"source": "bronze_products", "target": "silver_products"},
                {"source": "bronze_orders", "target": "silver_orders"},
                {"source": "bronze_order_items", "target": "silver_order_items"},
                {"source": "bronze_payments", "target": "silver_payments"},
                {"source": "bronze_events", "target": "silver_events"},
                {"source": "bronze_inventory", "target": "silver_inventory"},
                
                {"source": "silver_orders", "target": "daily_revenue"},
                {"source": "silver_payments", "target": "daily_revenue"},
                {"source": "silver_orders", "target": "daily_orders"},
                {"source": "silver_customers", "target": "customer_metrics"},
                {"source": "silver_orders", "target": "customer_metrics"},
                {"source": "silver_products", "target": "product_metrics"},
                {"source": "silver_order_items", "target": "product_metrics"},
                {"source": "silver_inventory", "target": "inventory_metrics"},
                
                {"source": "daily_revenue", "target": "api_metrics"},
                {"source": "daily_orders", "target": "api_metrics"},
                {"source": "customer_metrics", "target": "api_metrics"},
                {"source": "product_metrics", "target": "api_metrics"},
                {"source": "inventory_metrics", "target": "api_metrics"},
                
                {"source": "silver_customers", "target": "api_quality"},
                {"source": "silver_products", "target": "api_quality"},
                {"source": "silver_orders", "target": "api_quality"},
                {"source": "silver_payments", "target": "api_quality"},
                {"source": "silver_inventory", "target": "api_quality"},
                
                {"source": "src_events", "target": "fabric_eventstream"},
                {"source": "fabric_eventstream", "target": "fabric_eventhouse"},
                {"source": "fabric_eventhouse", "target": "api_anomalies"},
            ]
            
            return {"nodes": nodes, "edges": edges}
            
        except Exception as e:
            print(f"Fabric Lineage Error: {e}")
            return {"nodes": [], "edges": []}

    def get_metrics(self, limit: int = 30) -> Dict[str, Any]:
        try:
            trend_query = f"""
            SELECT TOP {limit}
                order_date as date,
                order_count as orders,
                daily_revenue as revenue,
                average_order_value
            FROM dbo.daily_revenue
            ORDER BY order_date DESC
            """
            trend_res = self._execute(trend_query)
            
            if not trend_res:
                return {"kpis": {}, "trend": []}

            total_orders = sum(row.get('orders', 0) for row in trend_res)
            total_revenue = sum(float(row.get('revenue', 0.0)) for row in trend_res)
            avg_order_value = (total_revenue / total_orders) if total_orders else 0
            
            min_date = min(row['date'] for row in trend_res)
            max_date = max(row['date'] for row in trend_res)
            
            cust_query = f"SELECT COUNT(DISTINCT customer_id) as cnt FROM dbo.silver_orders WHERE order_date >= '{min_date}' AND order_date <= '{max_date}'"
            cust_res = self._execute(cust_query)
            unique_customers = cust_res[0]['cnt'] if cust_res else 0
            
            return {
                "kpis": {
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "average_order_value": avg_order_value,
                    "unique_customers": unique_customers,
                    "period_label": f"{min_date} to {max_date}"
                },
                "trend": trend_res
            }
        except Exception as e:
            print(f"Fabric Metrics Error: {e}")
            return {"kpis": {}, "trend": []}


def get_data_provider() -> DataProvider:
    if EXECUTION_MODE == "fabric":
        return FabricProvider()

    return LocalDuckDBProvider()