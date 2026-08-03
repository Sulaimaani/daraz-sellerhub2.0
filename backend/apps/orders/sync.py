import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from django.db import transaction

from apps.stores.models import Store
from apps.products.models import Product, Sku
from apps.orders.models import Customer, Order, OrderItem
from apps.finance.models import FinanceTransaction
from apps.returns.models import ReturnPackage, ReturnItem

from apps.core.daraz.client import DarazClient
from apps.core.daraz.mapping import (
    map_order_and_customer,
    map_order_item,
    derive_order_status,
    map_product,
    map_finance_transaction,
    map_return_package,
)

logger = logging.getLogger(__name__)

def upsert_products(store: Store, products_payload: List[Dict[str, Any]]):
    """
    Upserts Products and SKUs. 
    Using update_conflicts=True (requires Django 4.1+) to ensure idempotency.
    """
    products_to_create = []
    skus_to_create = []
    
    # Track products we parse to associate SKUs accurately
    parsed_products = [] 
    
    for payload in products_payload:
        p_kwargs, s_list_kwargs = map_product(payload, store.id)
        
        product = Product(**p_kwargs)
        products_to_create.append(product)
        parsed_products.append((product, s_list_kwargs))
        
    if not products_to_create:
        return
        
    # Upsert Products
    Product.objects.bulk_create(
        products_to_create,
        update_conflicts=True,
        unique_fields=['store', 'daraz_item_id'],
        update_fields=['name', 'primary_category', 'brand', 'status', 'main_image_url', 'url', 'raw_json', 'updated_at']
    )
    
    # Fetch them back to get IDs for SKUs
    daraz_item_ids = [p.daraz_item_id for p in products_to_create]
    db_products = {p.daraz_item_id: p for p in Product.objects.filter(store=store, daraz_item_id__in=daraz_item_ids)}
    
    for product_obj, s_list_kwargs in parsed_products:
        db_product = db_products.get(product_obj.daraz_item_id)
        if not db_product:
            continue
        for sku_kwargs in s_list_kwargs:
            sku_kwargs['product_id'] = db_product.id
            skus_to_create.append(Sku(**sku_kwargs))
            
    if skus_to_create:
        Sku.objects.bulk_create(
            skus_to_create,
            update_conflicts=True,
            unique_fields=['store', 'seller_sku'],
            update_fields=[
                'daraz_sku_id', 'shop_sku', 'name', 'variation', 'price', 
                'special_price', 'quantity', 'image_url', 'package_weight',
                'package_length', 'package_width', 'package_height', 'raw_json', 'updated_at'
            ]
        )


def sync_products_window(store: Store):
    """Full catalog pull via /products/get"""
    client = DarazClient(store)
    offset = 0
    limit = 50
    has_more = True
    
    with transaction.atomic():
        while has_more:
            resp = client.call("/products/get", params={"limit": limit, "offset": offset, "filter": "all"})
            data = resp.get("data", {})
            products = data.get("products", [])
            
            if not products:
                break
                
            upsert_products(store, products)
            
            # offset pagination
            total = data.get("total_products", 0)
            offset += limit
            if offset >= total:
                has_more = False

def upsert_orders(store: Store, orders_payload: List[Dict[str, Any]], order_items_payload_map: Dict[str, List[Dict[str, Any]]]):
    """
    Upserts Customers, Orders, and OrderItems.
    """
    customers_dict = {}
    orders_to_create = []
    
    for order_payload in orders_payload:
        o_kwargs, c_kwargs = map_order_and_customer(order_payload, store.id)
        
        # Deduplicate customers in memory before upsert
        hashed_id = c_kwargs['hashed_identifier']
        if hashed_id not in customers_dict:
            customers_dict[hashed_id] = Customer(**c_kwargs)
            
        orders_to_create.append((Order(**o_kwargs), o_kwargs['daraz_order_id'], hashed_id))
        
    if not orders_to_create:
        return
        
    # Upsert Customers
    Customer.objects.bulk_create(
        customers_dict.values(),
        update_conflicts=True,
        unique_fields=['store', 'hashed_identifier'],
        update_fields=['name', 'phone', 'email', 'address_line', 'city', 'postcode', 'country', 'raw_json', 'updated_at']
    )
    
    # Fetch Customers back
    hashed_ids = list(customers_dict.keys())
    db_customers = {c.hashed_identifier: c for c in Customer.objects.filter(store=store, hashed_identifier__in=hashed_ids)}
    
    # Link Orders to Customers
    final_orders = []
    for order_obj, daraz_order_id, hashed_id in orders_to_create:
        if hashed_id in db_customers:
            order_obj.customer_id = db_customers[hashed_id].id
        final_orders.append(order_obj)
        
    # Upsert Orders
    Order.objects.bulk_create(
        final_orders,
        update_conflicts=True,
        unique_fields=['store', 'daraz_order_id'],
        update_fields=[
            'customer_id', 'status', 'raw_status_list', 'payment_method', 'is_cod',
            'price', 'shipping_fee', 'voucher', 'voucher_platform', 'voucher_seller',
            'tax_amount', 'items_count', 'created_at_daraz', 'updated_at_daraz',
            'promised_shipping_time', 'delivery_info', 'remarks', 'raw_json', 'updated_at'
        ]
    )
    
    # Fetch Orders back
    daraz_order_ids = [o.daraz_order_id for o, _, _ in orders_to_create]
    db_orders = {o.daraz_order_id: o for o in Order.objects.filter(store=store, daraz_order_id__in=daraz_order_ids)}
    
    # Pre-fetch SKUs to link OrderItems
    # First gather all seller_skus from the items map
    seller_skus = set()
    for _, items in order_items_payload_map.items():
        for item in items:
            if item.get('sku'):
                seller_skus.add(item.get('sku'))
                
    db_skus = {s.seller_sku: s for s in Sku.objects.filter(store=store, seller_sku__in=seller_skus)}
    
    # Prepare Order Items
    order_items_to_create = []
    for daraz_order_id, items_payload in order_items_payload_map.items():
        db_order = db_orders.get(str(daraz_order_id))
        if not db_order:
            continue
            
        ui_statuses = []
        for item_payload in items_payload:
            item_kwargs = map_order_item(item_payload, store.id, db_order.id)
            ui_statuses.append(item_kwargs['status'])
            
            # Link SKU
            seller_sku = item_kwargs['sku_string']
            if seller_sku in db_skus:
                item_kwargs['sku_id'] = db_skus[seller_sku].id
                
            order_items_to_create.append(OrderItem(**item_kwargs))
            
        # Update Order's overall status based on items
        db_order.raw_status_list = ui_statuses
        db_order.status = derive_order_status(ui_statuses)
        db_order.save(update_fields=['status', 'raw_status_list', 'updated_at'])
        
    if order_items_to_create:
        OrderItem.objects.bulk_create(
            order_items_to_create,
            update_conflicts=True,
            unique_fields=['store', 'daraz_order_item_id'],
            update_fields=[
                'sku_id', 'name', 'sku_string', 'shop_sku', 'variation',
                'item_price', 'paid_price', 'currency', 'tax_amount', 'shipping_amount',
                'shipping_service_cost', 'voucher_amount', 'voucher_code', 'status',
                'shipment_provider', 'tracking_code', 'package_id', 'shipping_type',
                'reason', 'reason_detail', 'is_digital', 'promised_shipping_time',
                'created_at_daraz', 'updated_at_daraz', 'sla_time_stamp', 'raw_json', 'updated_at'
            ]
        )


def sync_orders_window(store: Store, created_after: datetime, created_before: datetime):
    """Fetches orders and their items within a time window"""
    client = DarazClient(store)
    offset = 0
    limit = 100
    has_more = True
    
    with transaction.atomic():
        while has_more:
            resp = client.call("/orders/get", params={
                "created_after": created_after.isoformat(),
                "created_before": created_before.isoformat(),
                "limit": limit,
                "offset": offset,
            })
            data = resp.get("data", {})
            orders = data.get("orders", [])
            
            if not orders:
                break
                
            # Now we must fetch items for these orders in batches of 50
            order_ids = [str(o['order_id']) for o in orders if 'order_id' in o]
            order_items_map = {}
            
            # Batch into 50s
            for i in range(0, len(order_ids), 50):
                batch_ids = order_ids[i:i+50]
                # API uses JSON array string for order_ids
                import json
                items_resp = client.call("/orders/items/get", params={"order_ids": json.dumps(batch_ids)})
                items_data = items_resp.get("data", [])
                
                # The response is an array of objects: {"order_id": 123, "order_items": [...]}
                for order_item_group in items_data:
                    oid = str(order_item_group.get('order_id'))
                    order_items_map[oid] = order_item_group.get('order_items', [])
            
            upsert_orders(store, orders, order_items_map)
            
            total = data.get("count", 0)
            offset += limit
            if offset >= total:
                has_more = False
                
def sync_finance_window(store: Store, start_date: datetime, end_date: datetime):
    client = DarazClient(store)
    offset = 0
    limit = 100
    has_more = True
    
    transactions_to_create = []
    
    with transaction.atomic():
        while has_more:
            # /finance/transaction/detail/get expects start_time/end_time in YYYY-MM-DD
            resp = client.call("/finance/transaction/detail/get", params={
                "start_time": start_date.strftime("%Y-%m-%d"),
                "end_time": end_date.strftime("%Y-%m-%d"),
                "limit": limit,
                "offset": offset,
                "trans_type": -1 # All types
            })
            data = resp.get("data", {})
            transactions = data.get("transactionList", [])
            if not transactions:
                break
                
            for payload in transactions:
                kwargs = map_finance_transaction(payload, store.id)
                transactions_to_create.append(FinanceTransaction(**kwargs))
                
            # Handle linking to Orders in DB (omitted for brevity, done via bulk lookups)
            
            # offset based on total (if provided, sometimes not, need to check length)
            if len(transactions) < limit:
                has_more = False
            else:
                offset += limit
                
        if transactions_to_create:
            FinanceTransaction.objects.bulk_create(
                transactions_to_create,
                update_conflicts=True,
                unique_fields=['store', 'transaction_number'],
                update_fields=[
                    'order_id', 'order_item_id', 'transaction_type', 'fee_name', 'statement_id',
                    'amount', 'vat_in_amount', 'wht_amount', 'transaction_date', 'paid_status',
                    'payment_ref_id', 'details', 'raw_json', 'updated_at'
                ]
            )

def sync_returns_window(store: Store):
    client = DarazClient(store)
    offset = 0
    limit = 50
    has_more = True
    
    packages_to_create = []
    items_to_create = []
    
    with transaction.atomic():
        while has_more:
            resp = client.call("/reverse/order/list", params={
                "limit": limit,
                "offset": offset,
            })
            data = resp.get("data", {})
            packages = data.get("items", [])
            if not packages:
                break
                
            # Process returns
            
            # offset
            if len(packages) < limit:
                has_more = False
            else:
                offset += limit
