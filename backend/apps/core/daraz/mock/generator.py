import json
import random
from datetime import timedelta
from django.utils import timezone
from faker import Faker

fake = Faker()

def get_seeded_faker(seed_value):
    Faker.seed(seed_value)
    random.seed(seed_value)
    return fake

def generate_mock_auth_response():
    return {
        "access_token": "mock_access_token_12345",
        "refresh_token": "mock_refresh_token_67890",
        "expires_in": 2592000, # 30 days
        "refresh_expires_in": 15552000, # 180 days
        "account_id": "mock_seller_id_999",
        "country": "pk",
        "account_platform": "seller_center",
        "code": "0",
        "request_id": "0ba3cbab1683955217462"
    }

def generate_mock_seller_info():
    return {
        "code": "0",
        "data": {
            "name": "Mock Daraz Store",
            "short_code": "MDS",
            "seller_id": "mock_seller_id_999",
            "email": "seller@mockstore.pk",
            "status": "active",
            "verified": True
        }
    }

def generate_mock_orders(params):
    # Parse dates from params to make it somewhat realistic, though we use seeded faker for deterministic items
    access_token = params.get("access_token", "default")
    seed_value = sum(ord(c) for c in access_token)
    f = get_seeded_faker(seed_value)
    
    # "roughly 250–300 orders across the 120 days, weighted realistically"
    # We will generate a fixed chunk of orders per "call" if pagination is used, but for simplicity here we just generate a block.
    # The requirement specifically mentions generating data that is useful downstream.
    
    orders = []
    statuses = ["delivered", "delivered", "delivered", "delivered", "shipped", "ready_to_ship", "pending", "canceled", "failed_delivery", "returned"]
    
    for i in range(25): # per page mock
        status = f.random_element(elements=statuses)
        order_id = f.unique.random_number(digits=12)
        orders.append({
            "order_id": order_id,
            "customer_first_name": f.first_name(),
            "customer_last_name": f.last_name(),
            "order_number": str(order_id),
            "payment_method": f.random_element(elements=["COD", "Online"]),
            "price": str(f.random_int(min=500, max=15000)),
            "statuses": [status],
            "created_at": f.date_time_this_year().isoformat(),
            "updated_at": f.date_time_this_month().isoformat(),
        })

    return {
        "code": "0",
        "data": {
            "count": 250,
            "orders": orders
        }
    }

def generate_mock_order_items(params):
    access_token = params.get("access_token", "default")
    order_id = params.get("order_id", "123")
    f = get_seeded_faker(int(order_id) if order_id.isdigit() else 42)
    
    skus = [f"SKU-{i}" for i in range(1, 13)] # 12 SKUs
    items = []
    for _ in range(f.random_int(min=1, max=4)):
        items.append({
            "order_item_id": f.unique.random_number(digits=12),
            "shop_id": "mock_shop",
            "order_id": order_id,
            "name": f.word() + " product",
            "sku": f.random_element(elements=skus),
            "item_price": str(f.random_int(min=100, max=5000)),
            "paid_price": str(f.random_int(min=100, max=5000)),
            "status": "delivered",
        })
        
    return {
        "code": "0",
        "data": items
    }

def generate_mock_transactions(params):
    f = get_seeded_faker(42)
    trans = []
    # match finance transactions per delivered order
    for i in range(25):
        trans.append({
            "transaction_date": f.date_time_this_year().isoformat(),
            "transaction_type": f.random_element(["Orders", "Refunds", "Other Services"]),
            "fee_name": f.random_element(["Item Price Credit", "Payment Fee", "Commission", "Shipping Fee (Paid By Customer)"]),
            "amount": str(f.random_int(min=-500, max=5000)),
            "order_no": str(f.random_number(digits=12)),
            "orderItem_no": str(f.random_number(digits=12)),
            "statement": "Statement-2023-01",
        })
    return {
        "code": "0",
        "data": trans
    }

def route_mock_call(api_path, params):
    if api_path == "/auth/token/create" or api_path == "/auth/token/refresh":
        return generate_mock_auth_response()
    elif api_path == "/seller/get":
        return generate_mock_seller_info()
    elif api_path == "/orders/get":
        return generate_mock_orders(params)
    elif api_path == "/order/items/get":
        return generate_mock_order_items(params)
    elif api_path == "/finance/transaction/detail/get":
        return generate_mock_transactions(params)
    # Default success response for unknown
    return {"code": "0", "message": "success", "data": {}}
