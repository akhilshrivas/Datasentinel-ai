import yaml
import polars as pl
from datetime import datetime
import uuid
import os

class DataQualityFramework:
    def __init__(self, contracts_dir="contracts"):
        self.contracts_dir = contracts_dir
        self.results = []
        self.run_id = str(uuid.uuid4())
        
    def load_contract(self, dataset_name):
        path = os.path.join(self.contracts_dir, f"{dataset_name}.yaml")
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            return yaml.safe_load(f)
            
    def validate_dataset(self, dataset_name, df):
        contract = self.load_contract(dataset_name)
        if not contract:
            print(f"No contract found for {dataset_name}. Skipping validation.")
            return
            
        print(f"Validating {dataset_name}...")
        
        for col_def in contract.get('columns', []):
            col = col_def['name']
            if col not in df.columns:
                self.record_result(dataset_name, f"missing_column_{col}", "FAIL", "HIGH", f"Column {col} is missing")
                continue
                
            # Null check
            if not col_def.get('nullable', True):
                null_count = df.select(pl.col(col).is_null().sum()).item()
                status = "PASS" if null_count == 0 else "FAIL"
                self.record_result(dataset_name, f"null_check_{col}", status, "HIGH", f"Found {null_count} nulls")
                
            # Unique check
            if col_def.get('unique', False):
                dup_count = df.select(pl.col(col).is_duplicated().sum()).item()
                status = "PASS" if dup_count == 0 else "FAIL"
                self.record_result(dataset_name, f"unique_check_{col}", status, "HIGH", f"Found {dup_count} duplicates")
                
            # Accepted values
            if 'accepted_values' in col_def:
                invalid_count = df.filter(~pl.col(col).is_in(col_def['accepted_values'])).height
                status = "PASS" if invalid_count == 0 else "FAIL"
                self.record_result(dataset_name, f"accepted_values_{col}", status, "HIGH", f"Found {invalid_count} invalid values")

            # Range check
            if 'minimum' in col_def:
                invalid_count = df.filter(pl.col(col) < col_def['minimum']).height
                status = "PASS" if invalid_count == 0 else "FAIL"
                self.record_result(dataset_name, f"minimum_value_{col}", status, "HIGH", f"Found {invalid_count} below minimum")
                
    def record_result(self, dataset, check_name, status, severity, message):
        self.results.append({
            "run_id": self.run_id,
            "dataset": dataset,
            "check_name": check_name,
            "status": status,
            "severity": severity,
            "failed_records": 0, # Simplify for now
            "execution_time": datetime.now().isoformat(),
            "message": message
        })
        
    def save_results(self, output_dir="data/gold"):
        if not self.results:
            return
        os.makedirs(output_dir, exist_ok=True)
        df = pl.DataFrame(self.results)
        
        output_path = f"{output_dir}/quality_results.parquet"
        if os.path.exists(output_path):
            existing_df = pl.read_parquet(output_path)
            df = pl.concat([existing_df, df])
            
        df.write_parquet(output_path)
        print(f"Saved {len(self.results)} quality results.")

if __name__ == "__main__":
    dq = DataQualityFramework()
    # In a real run, you'd iterate through Silver datasets
    silver_dir = "data/silver"
    if os.path.exists(silver_dir):
        for file in os.listdir(silver_dir):
            if file.endswith(".parquet"):
                dataset_name = file.replace(".parquet", "")
                df = pl.read_parquet(os.path.join(silver_dir, file))
                dq.validate_dataset(dataset_name, df)
    dq.save_results()
