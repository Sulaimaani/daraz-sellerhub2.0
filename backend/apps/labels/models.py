from django.db import models
from apps.stores.models import Store
from apps.orders.models import Order

class LabelTemplate(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name='label_templates')
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    
    page_size = models.CharField(max_length=50, default='4x6in') # A6, A5, 4x6in, Custom
    width_mm = models.FloatField(default=101.6) # 4 inches
    height_mm = models.FloatField(default=152.4) # 6 inches
    dpi = models.IntegerField(default=300)
    
    canvas_json = models.JSONField(default=dict)
    version = models.IntegerField(default=1)
    
    created_by = models.CharField(max_length=255, blank=True)
    is_starter = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'name'], name='unique_store_label_template')
        ]

    def __str__(self):
        return f"{self.name} - Store {self.store_id}"

class LabelAsset(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='label_assets')
    kind = models.CharField(max_length=50) # logo, watermark, sticker
    file = models.FileField(upload_to='label_assets/')
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    checksum = models.CharField(max_length=64)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'checksum'], name='unique_store_label_asset')
        ]

    def __str__(self):
        return f"Asset {self.kind} - {self.checksum[:8]}"

class LabelJob(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='label_jobs')
    template = models.ForeignKey(LabelTemplate, on_delete=models.SET_NULL, null=True)
    
    order_ids = models.JSONField(default=list) # Array of order DB IDs
    status = models.CharField(max_length=50, default='queued') # queued, rendering, done, failed
    output_kind = models.CharField(max_length=50, default='merged_pdf') # merged_pdf, individual, zip
    
    progress_pct = models.IntegerField(default=0)
    output_file = models.FileField(upload_to='label_outputs/', null=True, blank=True)
    page_count = models.IntegerField(default=0)
    error = models.TextField(blank=True)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job {self.id} - {self.status}"

class LabelJobItem(models.Model):
    job = models.ForeignKey(LabelJob, on_delete=models.CASCADE, related_name='items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    package_id = models.CharField(max_length=255)
    
    status = models.CharField(max_length=50, default='pending')
    error = models.TextField(blank=True)
    page_index = models.IntegerField(default=0)
    
    def __str__(self):
        return f"JobItem {self.id} for Order {self.order_id}"
