# Fabric Lakehouse Delta Table Creation Script
# Run this in a Microsoft Fabric Spark Notebook

from pyspark.sql.types import *

# Define Schemas
customers_schema = StructType([
    StructField("customer_id", StringType(), False),
    StructField("email", StringType(), True),
    StructField("segment", StringType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("_run_id", StringType(), False),
    StructField("_ingest_ts", TimestampType(), False)
])

# Utility to create empty Delta table
def create_delta_table(table_name, schema, partition_col=None):
    df = spark.createDataFrame([], schema)
    writer = df.write.format("delta").mode("ignore")
    if partition_col:
        writer = writer.partitionBy(partition_col)
    writer.saveAsTable(table_name)
    print(f"Verified Delta table: {table_name}")

# Create Silver Tables
create_delta_table("silver_customers", customers_schema)

daily_revenue_schema = StructType([
    StructField("date", DateType(), False),
    StructField("total_revenue", DoubleType(), True),
    StructField("total_orders", IntegerType(), True),
    StructField("_run_id", StringType(), False)
])

# Create Gold Tables
create_delta_table("gold_daily_revenue", daily_revenue_schema, partition_col="date")
create_delta_table("gold_pipeline_runs", StructType([
    StructField("run_id", StringType(), False),
    StructField("pipeline_name", StringType(), True),
    StructField("start_time", TimestampType(), True),
    StructField("duration_sec", IntegerType(), True),
    StructField("records", IntegerType(), True),
    StructField("status", StringType(), True)
]))
create_delta_table("gold_anomalies", StructType([
    StructField("anomaly_id", StringType(), False),
    StructField("timestamp", TimestampType(), True),
    StructField("metric", StringType(), True),
    StructField("value", DoubleType(), True),
    StructField("baseline_value", DoubleType(), True),
    StructField("severity", StringType(), True)
]), partition_col="metric")

print("Fabric Lakehouse tables initialized successfully.")
