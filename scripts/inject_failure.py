import argparse
import polars as pl
import os
import random

SILVER_DIR = "data/silver"

def inject_nulls():
    path = f"{SILVER_DIR}/orders.parquet"
    if not os.path.exists(path):
        print("Orders not found.")
        return
    df = pl.read_parquet(path)
    # Inject nulls into total_amount randomly
    mask = [random.random() > 0.9 for _ in range(df.height)]
    df = df.with_columns(
        pl.when(pl.Series(mask)).then(None).otherwise(pl.col("total_amount")).alias("total_amount")
    )
    df.write_parquet(path)
    print("Injected nulls into orders total_amount.")

def inject_revenue_drop():
    path = f"{SILVER_DIR}/orders.parquet"
    if not os.path.exists(path):
        return
    df = pl.read_parquet(path)
    # Cut recent revenue in half
    df = df.with_columns(
        (pl.col("total_amount") * 0.1).alias("total_amount")
    )
    df.write_parquet(path)
    print("Injected revenue drop.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["nulls", "duplicates", "schema-drift", "revenue-drop", "late-data"], required=True)
    args = parser.parse_args()
    
    if args.type == "nulls":
        inject_nulls()
    elif args.type == "revenue-drop":
        inject_revenue_drop()
    else:
        print(f"Injection type {args.type} not fully implemented in this script.")
