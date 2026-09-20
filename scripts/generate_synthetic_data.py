import os
import json
import random
import uuid
from datetime import datetime, timedelta
import pandas as pd

DATA_DIR = "data/raw"

def generate_customers(n=1000):
    customers = []
    for _ in range(n):
        customers.append({
            "customer_id": str(uuid.uuid4()),
            "name": f"Customer {random.randint(1, 10000)}",
            "email": f"customer{random.randint(1, 10000)}@example.com",
            "signup_date": (datetime.now() - timedelta(days=random.randint(10, 365))).isoformat(),
            "tier": random.choice(["Bronze", "Silver", "Gold"])
        })
    return pd.DataFrame(customers)

def generate_products(n=100):
    products = []
    categories = ["Electronics", "Clothing", "Home", "Toys", "Sports"]
    for i in range(n):
        products.append({
            "product_id": str(uuid.uuid4()),
            "name": f"Product {i}",
            "category": random.choice(categories),
            "price": round(random.uniform(10.0, 500.0), 2),
            "cost": round(random.uniform(5.0, 200.0), 2)
        })
    return pd.DataFrame(products)

def generate_orders_and_items(customers, products, n_orders=5000):
    orders = []
    order_items = []
    payments = []
    events = []
    
    for _ in range(n_orders):
        order_id = str(uuid.uuid4())
        customer_id = random.choice(customers["customer_id"])
        order_date = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        # Order items
        n_items = random.randint(1, 5)
        total_amount = 0
        for _ in range(n_items):
            product = products.iloc[random.randint(0, len(products)-1)]
            quantity = random.randint(1, 3)
            price = product["price"]
            total_amount += price * quantity
            
            order_items.append({
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price": price
            })
            
        status = random.choices(["completed", "cancelled", "pending"], weights=[0.8, 0.1, 0.1])[0]
        orders.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date.isoformat(),
            "status": status,
            "total_amount": round(total_amount, 2)
        })
        
        # Payments
        if status != "pending":
            payments.append({
                "payment_id": str(uuid.uuid4()),
                "order_id": order_id,
                "amount": round(total_amount, 2),
                "payment_method": random.choice(["credit_card", "paypal", "store_credit"]),
                "status": "successful" if status == "completed" else "refunded",
                "payment_date": (order_date + timedelta(minutes=random.randint(1, 60))).isoformat()
            })
            
        # Events
        events.append({
            "event_id": str(uuid.uuid4()),
            "event_type": "order_created",
            "timestamp": order_date.isoformat(),
            "entity_id": order_id,
            "payload": json.dumps({"customer_id": customer_id, "amount": total_amount})
        })
        
    return pd.DataFrame(orders), pd.DataFrame(order_items), pd.DataFrame(payments), pd.DataFrame(events)

def generate_inventory(products):
    inventory = []
    for _, product in products.iterrows():
        inventory.append({
            "product_id": product["product_id"],
            "stock_level": random.randint(0, 1000),
            "last_updated": datetime.now().isoformat()
        })
    return pd.DataFrame(inventory)

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    print("Generating synthetic data...")
    customers = generate_customers()
    products = generate_products()
    orders, order_items, payments, events = generate_orders_and_items(customers, products)
    inventory = generate_inventory(products)
    
    customers.to_parquet(f"{DATA_DIR}/customers.parquet")
    products.to_parquet(f"{DATA_DIR}/products.parquet")
    orders.to_parquet(f"{DATA_DIR}/orders.parquet")
    order_items.to_parquet(f"{DATA_DIR}/order_items.parquet")
    payments.to_parquet(f"{DATA_DIR}/payments.parquet")
    events.to_parquet(f"{DATA_DIR}/events.parquet")
    inventory.to_parquet(f"{DATA_DIR}/inventory.parquet")
    
    print(f"Data generation complete. Saved to {DATA_DIR}/")

if __name__ == "__main__":
    main()
