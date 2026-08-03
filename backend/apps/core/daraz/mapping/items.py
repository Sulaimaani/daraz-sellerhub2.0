from typing import Dict, Any, List
from django.utils.dateparse import parse_datetime
from .base import check_unknown_fields, safe_decimal, safe_int, safe_bool

KNOWN_ITEM_FIELDS = [
    "order_item_id", "shop_id", "order_id", "name", "sku", "shop_sku", 
    "shipping_type", "item_price", "paid_price", "currency", "tax_amount", 
    "shipping_amount", "shipping_service_cost", "voucher_amount", "voucher_code", 
    "status", "is_digital", "tracking_code", "shipment_provider", "package_id", 
    "promised_shipping_time", "created_at", "updated_at", "sla_time_stamp",
    "cancel_return_initiator", "reason", "reason_detail", "variation", 
    "product_id"
]

def map_item_status(daraz_status: str) -> str:
    """Maps a raw Daraz item status into one of our 7 UI buckets."""
    # TODO: verify against live API if there are other undocumented statuses.
    status = daraz_status.lower()
    
    if status == 'unpaid':
        return 'Unpaid'
    elif status in ('pending', 'ready_to_ship'):
        return 'To Ship'
    elif status in ('shipped', 'in_transit', 'out_for_delivery'):
        return 'Shipping'
    elif status == 'delivered':
        return 'Delivered'
    elif status in ('failed', 'failed_delivery', 'lost', 'damaged_by_3pl'):
        return 'Failed Delivery'
    elif status in ('canceled', 'cancelled'):
        return 'Cancellation'
    elif status in ('returned', 'return_initiated', 'refunded', 'return_shipped_by_buyer', 'return_rejected'):
        return 'Return / Refund'
        
    return 'Unknown' # Fallback for newly discovered schema drift

def derive_order_status(item_ui_statuses: List[str]) -> str:
    """
    Derives the overall order status from a list of mapped UI statuses.
    Precedence: 
    Return/Refund > Failed Delivery > Shipping > To Ship > Unpaid > Delivered > Cancellation
    """
    if not item_ui_statuses:
        return 'Unknown'
        
    precedence = {
        'Return / Refund': 1,
        'Failed Delivery': 2,
        'Shipping': 3,
        'To Ship': 4,
        'Unpaid': 5,
        'Delivered': 6,
        'Cancellation': 7,
        'Unknown': 99
    }
    
    # Sort statuses by precedence and return the highest priority (lowest number)
    sorted_statuses = sorted(item_ui_statuses, key=lambda s: precedence.get(s, 99))
    return sorted_statuses[0]

def map_order_item(payload: Dict[str, Any], store_id: int, order_id: int) -> Dict[str, Any]:
    check_unknown_fields(payload, KNOWN_ITEM_FIELDS, "OrderItem")
    
    # Parse dates
    created_at = parse_datetime(payload.get('created_at', '')) if payload.get('created_at') else None
    updated_at = parse_datetime(payload.get('updated_at', '')) if payload.get('updated_at') else None
    promised = parse_datetime(payload.get('promised_shipping_time', '')) if payload.get('promised_shipping_time') else None
    sla = parse_datetime(payload.get('sla_time_stamp', '')) if payload.get('sla_time_stamp') else None
    
    daraz_status = payload.get('status', '')
    ui_status = map_item_status(daraz_status)
    
    return {
        "store_id": store_id,
        "order_id": order_id, # Internal Django ID for the order
        "daraz_order_item_id": str(payload.get('order_item_id', '')),
        "name": payload.get('name', ''),
        "sku_string": payload.get('sku', ''),
        "shop_sku": payload.get('shop_sku', ''),
        "variation": payload.get('variation', ''),
        
        "item_price": safe_decimal(payload.get('item_price')),
        "paid_price": safe_decimal(payload.get('paid_price')),
        "currency": payload.get('currency', ''),
        "tax_amount": safe_decimal(payload.get('tax_amount')),
        "shipping_amount": safe_decimal(payload.get('shipping_amount')),
        "shipping_service_cost": safe_decimal(payload.get('shipping_service_cost')),
        "voucher_amount": safe_decimal(payload.get('voucher_amount')),
        "voucher_code": payload.get('voucher_code', ''),
        
        "status": ui_status, # Use the mapped bucket directly
        "shipment_provider": payload.get('shipment_provider', ''),
        "tracking_code": payload.get('tracking_code', ''),
        "package_id": payload.get('package_id', ''),
        "shipping_type": payload.get('shipping_type', ''),
        
        "reason": payload.get('reason', ''),
        "reason_detail": payload.get('reason_detail', ''),
        "is_digital": safe_bool(payload.get('is_digital')),
        
        "promised_shipping_time": promised,
        "created_at_daraz": created_at,
        "updated_at_daraz": updated_at,
        "sla_time_stamp": sla,
        
        "raw_json": payload,
    }
