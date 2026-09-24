# Fabric Eventstream

The Eventstream acts as the real-time ingestion layer, replacing local JSON logs with scalable cloud streams.

## Event Schema

All events share a common payload envelope:
`json
{
  "event_id": "uuid",
  "event_type": "string",
  "timestamp": "iso8601",
  "payload": { ... }
}
`

### Event Types
1. order_created: {"order_id": "...", "amount": 100.0}
2. payment_completed: {"payment_id": "...", "order_id": "..."}
3. inventory_updated: {"product_id": "...", "new_stock": 50}
4. order_cancelled: {"order_id": "...", "reason": "..."}

## Implementation
The existing local Python event simulator can be configured to push to the Eventstream Custom App endpoint.
