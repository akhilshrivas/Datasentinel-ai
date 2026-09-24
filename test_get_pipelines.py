import os
os.environ["EXECUTION_MODE"] = "fabric"
from agents.tools import get_pipeline_status
import json

data = get_pipeline_status()
print(json.dumps(data, indent=2))
