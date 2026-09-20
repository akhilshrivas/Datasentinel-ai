import time
import json
import uuid
import random
from datetime import datetime

EVENTS = ["order_created", "payment_completed", "inventory_updated", "customer_updated", "order_cancelled"]

def simulate_events(duration_seconds=10, interval_seconds=1):
    start_time = time.time()
    print("Starting event simulation...")
    
    with open("data/raw/streaming_events.jsonl", "w") as f:
        while time.time() - start_time < duration_seconds:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_type": random.choice(EVENTS),
                "timestamp": datetime.now().isoformat(),
                "entity_id": str(uuid.uuid4()),
                "payload": {"random_metric": random.randint(1, 100)}
            }
            f.write(json.dumps(event) + "\n")
            f.flush()
            print(f"Produced event: {event['event_type']}")
            time.sleep(interval_seconds)
            
if __name__ == "__main__":
    simulate_events()
