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

class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.date} - {self.name}"

class PackageInspection(models.Model):
    return_package = models.ForeignKey(ReturnPackage, on_delete=models.CASCADE, related_name='inspections')
    item = models.ForeignKey(ReturnItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspections')
    
    # received_ok/damaged/wrong_item/missing/accessories_missing/package_not_received
    condition = models.CharField(max_length=100)
    recorded_by = models.CharField(max_length=255, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)
    photos = models.JSONField(default=list) # Array of URLs or references
    
    def __str__(self):
        return f"Inspection for {self.return_package_id}: {self.condition}"

class ReturnClaim(models.Model):
    return_package = models.ForeignKey(ReturnPackage, on_delete=models.CASCADE, related_name='claims')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='claims')
    
    claim_type = models.CharField(max_length=100)
    condition_recorded = models.CharField(max_length=100, blank=True)
    
    # draft/submitted/pending/approved/partially_approved/rejected/appealed/expired
    status = models.CharField(max_length=50, default='draft')
    filed_at = models.DateTimeField(null=True, blank=True)
    is_late_filing = models.BooleanField(default=False)
    
    expected_refund = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    daraz_claim_ref = models.CharField(max_length=255, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    deadline_at = models.DateTimeField(null=True, blank=True)
    deadline_source_field = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Claim for {self.return_package_id} ({self.status})"

class ClaimEvidence(models.Model):
    claim = models.ForeignKey(ReturnClaim, on_delete=models.CASCADE, related_name='evidence')
    kind = models.CharField(max_length=50) # image/video/document
    file = models.FileField(upload_to='claims/evidence/')
    caption = models.CharField(max_length=500, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    checksum = models.CharField(max_length=64, blank=True)
    exif_stripped = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Evidence for Claim {self.claim_id}"

class ClaimStatusEvent(models.Model):
    claim = models.ForeignKey(ReturnClaim, on_delete=models.CASCADE, related_name='status_events')
    from_status = models.CharField(max_length=50, blank=True)
    to_status = models.CharField(max_length=50)
    
    actor = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.from_status} -> {self.to_status} on Claim {self.claim_id}"
