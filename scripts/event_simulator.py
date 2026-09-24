import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from azure.eventhub import EventData, EventHubProducerClient

load_dotenv()

CONNECTION_STRING = os.getenv("FABRIC_EVENTHUB_CONNECTION_STRING")

if not CONNECTION_STRING:
    raise RuntimeError(
        "FABRIC_EVENTHUB_CONNECTION_STRING is missing from .env"
    )

EVENTS = [
    "order_created",
    "payment_completed",
    "inventory_updated",
    "customer_updated",
    "order_cancelled",
]


def build_event():
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(EVENTS),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entity_id": str(uuid.uuid4()),
        "payload": {
            "random_metric": random.randint(1, 100),
            "source": "datasentinel-simulator",
        },
    }


def send_events(duration_seconds=30, interval_seconds=2):
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STRING
    )

    start_time = time.time()

    print("Starting Fabric Eventstream simulation...")

    with producer:
        while time.time() - start_time < duration_seconds:
            event = build_event()

            batch = producer.create_batch()
            batch.add(EventData(json.dumps(event)))

            producer.send_batch(batch)

            print(
                f"Sent: {event['event_type']} | "
                f"{event['timestamp']}"
            )

            time.sleep(interval_seconds)

    print("Simulation finished.")


if __name__ == "__main__":
    send_events()