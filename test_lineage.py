import os
os.environ["EXECUTION_MODE"] = "fabric"
from apps.api.data_provider import get_data_provider
import json

provider = get_data_provider()
data = provider.get_lineage()
print(json.dumps(data, indent=2))
