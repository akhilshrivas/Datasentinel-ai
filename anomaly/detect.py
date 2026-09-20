import os
import polars as pl
import uuid
from datetime import datetime
import numpy as np

GOLD_DIR = "data/gold"

def detect_revenue_anomalies():
    revenue_path = f"{GOLD_DIR}/daily_revenue.parquet"
    if not os.path.exists(revenue_path):
        print("No daily_revenue data to analyze.")
        return []

    df = pl.read_parquet(revenue_path)
    if df.height < 3:
        return []
        
    df = df.sort("date")
    # Calculate rolling mean and std
    mean_val = df["revenue"].mean()
    std_val = df["revenue"].std()
    
    anomalies = []
    
    for row in df.iter_rows(named=True):
        rev = row["revenue"]
        z_score = (rev - mean_val) / std_val if std_val > 0 else 0
        
        if abs(z_score) > 2.0:
            anomalies.append({
                "anomaly_id": str(uuid.uuid4()),
                "metric": "daily_revenue",
                "timestamp": row["date"].isoformat(),
                "actual_value": rev,
                "baseline_value": mean_val,
                "percentage_change": ((rev - mean_val) / mean_val) * 100 if mean_val > 0 else 0,
                "severity": "HIGH" if abs(z_score) > 3 else "MEDIUM",
                "detection_method": "z-score",
                "status": "DETECTED"
            })
            
    return anomalies

def save_anomalies(anomalies):
    if not anomalies:
        print("No anomalies detected.")
        return
        
    df = pl.DataFrame(anomalies)
    output_path = f"{GOLD_DIR}/anomalies.parquet"
    
    if os.path.exists(output_path):
        existing_df = pl.read_parquet(output_path)
        df = pl.concat([existing_df, df])
        
    df.write_parquet(output_path)
    print(f"Saved {len(anomalies)} anomalies to {output_path}.")

if __name__ == "__main__":
    anomalies = detect_revenue_anomalies()
    save_anomalies(anomalies)
