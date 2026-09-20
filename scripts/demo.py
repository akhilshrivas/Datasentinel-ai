import os
import time
import subprocess

def run_step(name, cmd):
    print(f"\n[{name}]")
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error in {name}: {result.stderr}")
        exit(1)
    print(f"Success: {name}")
    print(result.stdout[:200] + "...\n")

def main():
    print("======================================")
    print(" DataSentinel AI Full Demo Scenario ")
    print("======================================\n")
    
    run_step("Generate Synthetic Data", ".\\venv\\Scripts\\python scripts/generate_synthetic_data.py")
    run_step("Process Bronze Layer", ".\\venv\\Scripts\\python pipelines/process_bronze.py")
    run_step("Process Silver & Gold Layers", ".\\venv\\Scripts\\python pipelines/process_silver_gold.py")
    run_step("Run Data Quality Framework", ".\\venv\\Scripts\\python quality/run_checks.py")
    run_step("Run Anomaly Detection", ".\\venv\\Scripts\\python anomaly/detect.py")
    
    print("\n[Injecting Failure]")
    run_step("Inject Revenue Drop Anomaly", ".\\venv\\Scripts\\python scripts/inject_failure.py --type revenue-drop")
    
    # Rerun gold to reflect revenue drop
    run_step("Reprocess Gold Layer", ".\\venv\\Scripts\\python pipelines/process_silver_gold.py")
    run_step("Run Anomaly Detection (Failure)", ".\\venv\\Scripts\\python anomaly/detect.py")
    
    print("\nDemo scenario complete! The system now contains a simulated revenue anomaly.")
    print("Start the API and ask the Agent to investigate.")

if __name__ == "__main__":
    main()
