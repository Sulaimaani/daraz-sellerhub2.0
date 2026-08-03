import json
from typing import Dict, Any, Tuple, List
from .base import check_unknown_fields, safe_decimal, safe_int

KNOWN_PRODUCT_FIELDS = [
    "item_id", "primary_category", "attributes", "skus", "created_time", "updated_time",
    "status", "suspended_reason", "marketImages"
]

KNOWN_SKU_FIELDS = [
    "Status", "quantity", "_compatible_variation_", "color_family", "size", 
    "price", "package_length", "package_height", "special_price", 
    "special_from_time", "special_to_time", "package_width", 
    "package_weight", "SkuId", "Available", "seller_sku", "shop_sku", 
    "Url", "Images", "package_content"
]

def map_product(payload: Dict[str, Any], store_id: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Returns (product_kwargs, [sku_kwargs_1, sku_kwargs_2, ...])
    """
    check_unknown_fields(payload, KNOWN_PRODUCT_FIELDS, "Product")
    
    attributes = payload.get('attributes', {})
    if isinstance(attributes, str):
        try:
            attributes = json.loads(attributes)
        except json.JSONDecodeError:
            attributes = {}
            
    name = attributes.get('name', 'Unknown')
    brand = attributes.get('brand', 'No Brand')
    
    product_kwargs = {
        "store_id": store_id,
        "daraz_item_id": str(payload.get('item_id', '')),
        "name": name,
        "primary_category": str(payload.get('primary_category', '')),
        "brand": brand,
        "status": payload.get('status', ''),
        # First image if exists, else empty
        "main_image_url": "", # Will populate if we find one in SKUs
        "url": "", # Populate if found
        "raw_json": payload,
    }
    
    sku_list_kwargs = []
    
    skus_payload = payload.get('skus', [])
    for sku_payload in skus_payload:
        check_unknown_fields(sku_payload, KNOWN_SKU_FIELDS, "Sku")
        
        # Build variation dict dynamically from keys that look like variations
        variation_keys = ['color_family', 'size', '_compatible_variation_']
        variation = {k: sku_payload[k] for k in variation_keys if k in sku_payload}
        
        # Extract images
        images = sku_payload.get('Images', [])
        image_url = images[0] if isinstance(images, list) and images else ""
        if image_url and not product_kwargs["main_image_url"]:
            product_kwargs["main_image_url"] = image_url
            
        if sku_payload.get('Url') and not product_kwargs["url"]:
            product_kwargs["url"] = sku_payload.get('Url')

        sku_kwargs = {
            "store_id": store_id,
            # "product_id" will be set dynamically by the caller after saving the Product
            "daraz_sku_id": str(sku_payload.get('SkuId', '')),
            "seller_sku": str(sku_payload.get('seller_sku', '')),
            "shop_sku": str(sku_payload.get('shop_sku', '')),
            "name": name,
            "variation": variation,
            "price": safe_decimal(sku_payload.get('price')),
            "special_price": safe_decimal(sku_payload.get('special_price')),
            "quantity": safe_int(sku_payload.get('quantity')),
            "image_url": image_url,
            "package_weight": str(sku_payload.get('package_weight', '')),
            "package_length": str(sku_payload.get('package_length', '')),
            "package_width": str(sku_payload.get('package_width', '')),
            "package_height": str(sku_payload.get('package_height', '')),
            "raw_json": sku_payload,
        }
        sku_list_kwargs.append(sku_kwargs)
        
    return product_kwargs, sku_list_kwargs
