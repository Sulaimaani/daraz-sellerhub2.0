import hashlib
from typing import Dict, Any, Tuple
from django.utils.dateparse import parse_datetime
from .base import check_unknown_fields, safe_decimal, safe_int, safe_bool

KNOWN_ORDER_FIELDS = [
    "order_id", "order_number", "payment_method", "remarks", "delivery_info",
    "statuses", "created_at", "updated_at", "promised_shipping_times",
    "items_count", "price", "shipping_fee", "voucher", "voucher_platform",
    "voucher_seller", "tax_amount", "national_registration_number",
    # Customer fields often bundled in Daraz order payload:
    "customer_first_name", "customer_last_name", "address_billing", "address_shipping",
]

def _hash_customer(identifier_string: str) -> str:
    """Deterministic hash for customer PII to avoid duplicate records."""
    return hashlib.sha256(identifier_string.encode('utf-8')).hexdigest()

def map_order_and_customer(payload: Dict[str, Any], store_id: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Returns (order_kwargs, customer_kwargs).
    """
    check_unknown_fields(payload, KNOWN_ORDER_FIELDS, "Order")
    
    # Customer Mapping
    first_name = payload.get('customer_first_name', '')
    last_name = payload.get('customer_last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    
    # Daraz usually provides address_shipping as a dict
    shipping = payload.get('address_shipping', {})
    phone = shipping.get('phone', '') if isinstance(shipping, dict) else ''
    address_line = shipping.get('address1', '') if isinstance(shipping, dict) else ''
    city = shipping.get('city', '') if isinstance(shipping, dict) else ''
    postcode = shipping.get('post_code', '') if isinstance(shipping, dict) else ''
    country = shipping.get('country', '') if isinstance(shipping, dict) else ''
    
    # TODO: verify against live API what exact fields are passed for Customer.
    identifier_string = f"{phone}-{full_name}-{address_line}"
    hashed_id = _hash_customer(identifier_string)
    
    customer_kwargs = {
        "store_id": store_id,
        "hashed_identifier": hashed_id,
        "name": full_name,
        "phone": phone,
        "address_line": address_line,
        "city": city,
        "postcode": postcode,
        "country": country,
        "raw_json": shipping,
    }
    
    # Order Mapping
    daraz_order_id = str(payload.get('order_id', ''))
    order_number = str(payload.get('order_number', ''))
    
    # Parse dates safely
    created_at = parse_datetime(payload.get('created_at', '')) if payload.get('created_at') else None
    updated_at = parse_datetime(payload.get('updated_at', '')) if payload.get('updated_at') else None
    
    # promised_shipping_times might be a string or list, we'll try to parse if it's a string
    pst = payload.get('promised_shipping_times')
    promised_shipping_time = parse_datetime(pst) if isinstance(pst, str) and pst else None
    
    order_kwargs = {
        "store_id": store_id,
        "daraz_order_id": daraz_order_id,
        "order_number": order_number,
        "payment_method": payload.get('payment_method', ''),
        # TODO: verify against live API if is_cod can be directly determined from payment_method
        "is_cod": payload.get('payment_method', '').lower() == 'cod',
        "price": safe_decimal(payload.get('price')),
        "shipping_fee": safe_decimal(payload.get('shipping_fee')),
        "voucher": safe_decimal(payload.get('voucher')),
        "voucher_platform": safe_decimal(payload.get('voucher_platform')),
        "voucher_seller": safe_decimal(payload.get('voucher_seller')),
        "tax_amount": safe_decimal(payload.get('tax_amount')),
        "items_count": safe_int(payload.get('items_count')),
        "created_at_daraz": created_at,
        "updated_at_daraz": updated_at,
        "promised_shipping_time": promised_shipping_time,
        "delivery_info": payload.get('delivery_info', ''),
        "remarks": payload.get('remarks', ''),
        "raw_json": payload,
    }
    
    return order_kwargs, customer_kwargs
