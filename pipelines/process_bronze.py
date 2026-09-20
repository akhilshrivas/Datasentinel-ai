import os
import uuid
import glob
from datetime import datetime
import polars as pl

RAW_DIR = "data/raw"
BRONZE_DIR = "data/bronze"

def process_bronze():
    os.makedirs(BRONZE_DIR, exist_ok=True)
    batch_id = str(uuid.uuid4())
    ingestion_time = datetime.now().isoformat()
    
    parquet_files = glob.glob(f"{RAW_DIR}/*.parquet")
    
    for file_path in parquet_files:
        filename = os.path.basename(file_path)
        dataset_name = filename.replace('.parquet', '')
        print(f"Processing {dataset_name} to Bronze...")
        
        df = pl.read_parquet(file_path)
        
        # Add metadata
        df = df.with_columns([
            pl.lit(batch_id).alias("_batch_id"),
            pl.lit(ingestion_time).alias("_ingestion_time"),
            pl.lit("local_file").alias("_source")
        ])
        
        output_path = f"{BRONZE_DIR}/{dataset_name}.parquet"
        df.write_parquet(output_path)
        print(f"Saved {output_path}")

if __name__ == "__main__":
    process_bronze()
