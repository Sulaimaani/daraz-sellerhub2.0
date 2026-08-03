from django.db import models
from apps.stores.models import Store
from apps.products.models import Sku

class Customer(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='customers')
    hashed_identifier = models.CharField(max_length=255) # SHA-256 for idempotency, no plaintext PII here
    
    # PII fields strictly masked in API list responses
    name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)
    email = models.CharField(max_length=255, blank=True)
    address_line = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'hashed_identifier'], name='unique_store_customer')
        ]

    def __str__(self):
        return f"Customer {self.hashed_identifier[:8]}"

class Order(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    daraz_order_id = models.CharField(max_length=255)
    order_number = models.CharField(max_length=255)
    
    # Derived from item statuses
    status = models.CharField(max_length=100)
    raw_status_list = models.JSONField(default=list)
    
    payment_method = models.CharField(max_length=100, blank=True)
    is_cod = models.BooleanField(default=False)
    
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    voucher = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    voucher_platform = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    voucher_seller = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    items_count = models.IntegerField(default=0)
    
    created_at_daraz = models.DateTimeField(null=True, blank=True)
    updated_at_daraz = models.DateTimeField(null=True, blank=True)
    promised_shipping_time = models.DateTimeField(null=True, blank=True)
    
    delivery_info = models.CharField(max_length=500, blank=True)
    remarks = models.TextField(blank=True)
    
    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'daraz_order_id'], name='unique_store_order')
        ]
        indexes = [
            models.Index(fields=['store', 'status', 'created_at_daraz']),
            models.Index(fields=['store', 'created_at_daraz']),
            models.Index(fields=['store', 'updated_at_daraz']),
        ]

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='order_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sku = models.ForeignKey(Sku, on_delete=models.SET_NULL, null=True, related_name='order_items')
    
    daraz_order_item_id = models.CharField(max_length=255)
    name = models.CharField(max_length=500)
    sku_string = models.CharField(max_length=255) # seller_sku raw string
    shop_sku = models.CharField(max_length=255, blank=True)
    variation = models.CharField(max_length=500, blank=True)
    
    item_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, blank=True)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_service_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    voucher_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    voucher_code = models.CharField(max_length=255, blank=True)
    
    status = models.CharField(max_length=100)
    shipment_provider = models.CharField(max_length=255, blank=True)
    tracking_code = models.CharField(max_length=255, blank=True)
    package_id = models.CharField(max_length=255, blank=True)
    shipping_type = models.CharField(max_length=100, blank=True)
    
    reason = models.CharField(max_length=500, blank=True)
    reason_detail = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    
    promised_shipping_time = models.DateTimeField(null=True, blank=True)
    created_at_daraz = models.DateTimeField(null=True, blank=True)
    updated_at_daraz = models.DateTimeField(null=True, blank=True)
    sla_time_stamp = models.DateTimeField(null=True, blank=True)
    
    # Profit Caching Fields
    profit_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    profit_confidence = models.CharField(max_length=50, blank=True) # FINAL, PROVISIONAL, INCOMPLETE
    profit_computed_at = models.DateTimeField(null=True, blank=True)

    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'daraz_order_item_id'], name='unique_store_order_item')
        ]
        indexes = [
            models.Index(fields=['store', 'status']),
            models.Index(fields=['store', 'tracking_code']),
            models.Index(fields=['store', 'package_id']),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.sku_string}"

class Shipment(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shipments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    
    package_id = models.CharField(max_length=255)
    tracking_code = models.CharField(max_length=255, blank=True)
    shipment_provider = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=100, blank=True)
    
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    label_url_cached = models.URLField(max_length=1000, blank=True)
    label_fetched_at = models.DateTimeField(null=True, blank=True)
    
    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'package_id'], name='unique_store_package')
        ]

    def __str__(self):
        return f"Pkg {self.package_id}"
