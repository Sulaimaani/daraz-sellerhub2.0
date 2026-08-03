import hashlib
from typing import Dict, Any
from django.utils.dateparse import parse_datetime
from .base import check_unknown_fields, safe_decimal

KNOWN_FINANCE_FIELDS = [
    "transaction_date", "transaction_type", "fee_name", "transaction_number", 
    "details", "seller_sku", "amount", "vat_in_amount", "wht_amount", 
    "statement_id", "paid_status", "order_no", "orderItem_no", "orderItem_status", 
    "payment_ref_id"
]

def _hash_transaction(payload: Dict[str, Any]) -> str:
    """Creates a deterministic hash for a transaction when Daraz gives no transaction_number."""
    date = payload.get('transaction_date', '')
    type_str = payload.get('transaction_type', '')
    fee = payload.get('fee_name', '')
    amt = str(payload.get('amount', ''))
    order = str(payload.get('order_no', ''))
    item = str(payload.get('orderItem_no', ''))
    
    unique_string = f"{date}-{type_str}-{fee}-{amt}-{order}-{item}"
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def map_finance_transaction(payload: Dict[str, Any], store_id: int) -> Dict[str, Any]:
    check_unknown_fields(payload, KNOWN_FINANCE_FIELDS, "FinanceTransaction")
    
    transaction_number = str(payload.get('transaction_number', '')).strip()
    if not transaction_number:
        transaction_number = f"HASH-{_hash_transaction(payload)}"
        
    date_str = payload.get('transaction_date', '')
    # Daraz finance date is usually "DD MMM YYYY" or ISO 8601, we might need a custom parser if it fails
    # For now parse_datetime usually handles standard ISO. 
    # TODO: verify against live API the exact date format for transaction_date.
    transaction_date = parse_datetime(date_str) if date_str else None
    
    return {
        "store_id": store_id,
        "transaction_number": transaction_number,
        # "order_id" and "order_item_id" are linked by the caller via DB lookups
        "transaction_type": payload.get('transaction_type', ''),
        "fee_name": payload.get('fee_name', ''),
        "statement_id": str(payload.get('statement_id', '')),
        
        "amount": safe_decimal(payload.get('amount')),
        "vat_in_amount": safe_decimal(payload.get('vat_in_amount')),
        "wht_amount": safe_decimal(payload.get('wht_amount')),
        
        "transaction_date": transaction_date,
        "paid_status": payload.get('paid_status', ''),
        "payment_ref_id": payload.get('payment_ref_id', ''),
        
        "details": payload.get('details', {}), # e.g. "Payment Fee" details
        "raw_json": payload,
    }
