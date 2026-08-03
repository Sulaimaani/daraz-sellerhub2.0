from typing import Dict, Any, Tuple, List
from django.utils.dateparse import parse_datetime
from .base import check_unknown_fields, safe_decimal, safe_int

KNOWN_RETURN_FIELDS = [
    "reverse_order_id", "order_id", "trade_order_id", "creation_time", "updated_time",
    "status", "reverse_status", "return_reason", "buyer_return_reason", 
    "refund_amount", "tracking_number", "shipment_provider", "package_type", 
    "is_full_package_return", "item_value_total", "items"
]

KNOWN_RETURN_ITEM_FIELDS = [
    "reverse_order_line_id", "trade_order_line_id", "product_id", "sku", 
    "name", "quantity", "quantity_returned", "quantity_ordered", 
    "item_value", "image", "status"
]

def map_return_package(payload: Dict[str, Any], store_id: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    check_unknown_fields(payload, KNOWN_RETURN_FIELDS, "ReturnPackage")
    
    daraz_status = payload.get('reverse_status', '') or payload.get('status', '')
    
    returned_at = parse_datetime(payload.get('creation_time', '')) if payload.get('creation_time') else None
    status_updated_at = parse_datetime(payload.get('updated_time', '')) if payload.get('updated_time') else None
    
    package_kwargs = {
        "store_id": store_id,
        "return_order_id": str(payload.get('reverse_order_id', '')),
        # "order_id" (Django ID) will be populated by caller
        "tracking_code": payload.get('tracking_number', ''),
        "package_type": payload.get('package_type', ''),
        
        "lifecycle_status": payload.get('status', ''),
        "daraz_status": daraz_status,
        "daraz_status_updated_at": status_updated_at,
        
        "returned_at": returned_at,
        # TODO: verify against live API how received_at is represented for seller warehouses
        "received_at": None,
        
        "reason": payload.get('return_reason', ''),
        "buyer_reason": payload.get('buyer_return_reason', ''),
        
        "item_value_total": safe_decimal(payload.get('item_value_total')),
        "refund_amount": safe_decimal(payload.get('refund_amount')),
        "is_full_package_return": bool(payload.get('is_full_package_return', True)),
        
        "raw_json": payload,
    }
    
    item_list_kwargs = []
    items_payload = payload.get('items', [])
    for item_payload in items_payload:
        check_unknown_fields(item_payload, KNOWN_RETURN_ITEM_FIELDS, "ReturnItem")
        
        item_kwargs = {
            "store_id": store_id,
            # "return_package_id" populated by caller
            # "order_item_id" populated by caller using trade_order_line_id
            "_trade_order_line_id": str(item_payload.get('trade_order_line_id', '')), # Transient field for linking
            
            "daraz_item_id": str(item_payload.get('product_id', '')),
            "sku_string": item_payload.get('sku', ''),
            "name": item_payload.get('name', ''),
            
            "quantity_returned": safe_int(item_payload.get('quantity_returned') or item_payload.get('quantity')),
            "quantity_ordered": safe_int(item_payload.get('quantity_ordered')),
            "item_value": safe_decimal(item_payload.get('item_value')),
            
            "image_url": item_payload.get('image', ''),
            "raw_json": item_payload,
        }
        item_list_kwargs.append(item_kwargs)
        
    return package_kwargs, item_list_kwargs
