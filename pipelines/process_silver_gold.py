import os
import polars as pl
from datetime import datetime

BRONZE_DIR = "data/bronze"
SILVER_DIR = "data/silver"
GOLD_DIR = "data/gold"

def process_silver():
    os.makedirs(SILVER_DIR, exist_ok=True)
    datasets = ["customers", "products", "orders", "order_items", "payments", "inventory"]
    
    for dataset in datasets:
        bronze_path = f"{BRONZE_DIR}/{dataset}.parquet"
        if not os.path.exists(bronze_path):
            print(f"Skipping {dataset}, bronze not found.")
            continue
            
        print(f"Processing {dataset} to Silver...")
        df = pl.read_parquet(bronze_path)
        
        # Basic cleaning: deduplication
        if "customer_id" in df.columns and dataset == "customers":
            df = df.unique(subset=["customer_id"])
        elif "product_id" in df.columns and dataset == "products":
            df = df.unique(subset=["product_id"])
        elif "order_id" in df.columns and dataset == "orders":
            df = df.unique(subset=["order_id"])
            
        # Standardize types and strings
        for col in df.columns:
            if df[col].dtype == pl.Utf8:
                df = df.with_columns(pl.col(col).str.strip_chars())
                
        df = df.with_columns(pl.lit(datetime.now().isoformat()).alias("_silver_processing_time"))
        df.write_parquet(f"{SILVER_DIR}/{dataset}.parquet")

def process_gold():
    os.makedirs(GOLD_DIR, exist_ok=True)
    print("Processing Gold tables...")
    
    orders = pl.read_parquet(f"{SILVER_DIR}/orders.parquet")
    order_items = pl.read_parquet(f"{SILVER_DIR}/order_items.parquet")
    products = pl.read_parquet(f"{SILVER_DIR}/products.parquet")
    customers = pl.read_parquet(f"{SILVER_DIR}/customers.parquet")
    
    # 1. Daily Revenue
    if "order_date" in orders.columns and "total_amount" in orders.columns:
        orders = orders.with_columns(pl.col("order_date").str.to_datetime().dt.date().alias("date"))
        daily_revenue = orders.group_by("date").agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("order_id").count().alias("order_count")
        ]).sort("date")
        daily_revenue.write_parquet(f"{GOLD_DIR}/daily_revenue.parquet")
        print("Created daily_revenue.")

    # 2. Product Metrics
    joined = order_items.join(orders, on="order_id", how="left", suffix="_orders").join(products, on="product_id", how="left", suffix="_products")
    product_metrics = joined.group_by("product_id").agg([
        pl.col("quantity").sum().alias("total_sold"),
        (pl.col("quantity") * pl.col("unit_price")).sum().alias("total_revenue")
    ])
    product_metrics.write_parquet(f"{GOLD_DIR}/product_metrics.parquet")
    print("Created product_metrics.")

if __name__ == "__main__":
    process_silver()
    process_gold()
