from django.db import models
from apps.stores.models import Store
from apps.orders.models import Order, OrderItem

class ReturnPackage(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='return_packages')
    return_order_id = models.CharField(max_length=255)
    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_packages')
    
    tracking_code = models.CharField(max_length=255, blank=True)
    package_type = models.CharField(max_length=100, blank=True) # full/partial
    
    lifecycle_status = models.CharField(max_length=100, blank=True) # high-level bucket if needed
    daraz_status = models.CharField(max_length=100, blank=True)
    daraz_status_updated_at = models.DateTimeField(null=True, blank=True)
    
    returned_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    
    reason = models.CharField(max_length=255, blank=True)
    buyer_reason = models.CharField(max_length=255, blank=True)
    
    item_value_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_full_package_return = models.BooleanField(default=True)
    
    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'return_order_id'], name='unique_store_return_pkg')
        ]
        indexes = [
            models.Index(fields=['store', 'daraz_status_updated_at']),
        ]

    def __str__(self):
        return f"Return {self.return_order_id}"

class ReturnItem(models.Model):
    return_package = models.ForeignKey(ReturnPackage, on_delete=models.CASCADE, related_name='items')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='return_items')
    
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='return_items')
    
    daraz_item_id = models.CharField(max_length=255, blank=True)
    sku_string = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=500, blank=True)
    
    quantity_returned = models.IntegerField(default=1)
    quantity_ordered = models.IntegerField(default=1)
    item_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    condition_recorded = models.CharField(max_length=255, null=True, blank=True) # Set in Phase 7
    image_url = models.URLField(max_length=1000, blank=True)

    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return Item {self.daraz_item_id}"
