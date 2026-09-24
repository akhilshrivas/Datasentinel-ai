import os
import time
os.environ["EXECUTION_MODE"] = "fabric"
from apps.api.data_provider import get_data_provider

provider = get_data_provider()

endpoints = [
    ("Lineage", provider.get_lineage),
    ("Overview/Metrics", provider.get_metrics),
    ("Pipelines", provider.get_pipeline_runs),
    ("Quality", provider.get_quality_latest),
    ("Anomalies", provider.get_anomalies)
]

print("--- STARTING API QA ---")
for name, func in endpoints:
    start = time.time()
    try:
        if name == "Lineage":
             # Avoid printing the huge graph, just measure lengths
             res = func()
             elapsed = time.time() - start
             print(f"PASS: {name} completed in {elapsed:.2f}s. Nodes: {len(res.get('nodes', []))}, Edges: {len(res.get('edges', []))}")
        elif name == "Overview/Metrics":
             res = func()
             elapsed = time.time() - start
             print(f"PASS: {name} completed in {elapsed:.2f}s. Trend length: {len(res.get('trend', []))}")
        else:
             res = func()
             elapsed = time.time() - start
             print(f"PASS: {name} completed in {elapsed:.2f}s. Count: {len(res)}")
    except Exception as e:
        print(f"FAIL: {name} failed with error {e}")
