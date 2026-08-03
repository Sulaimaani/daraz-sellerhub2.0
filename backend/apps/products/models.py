from django.db import models
from apps.stores.models import Store

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    daraz_item_id = models.CharField(max_length=255)
    name = models.CharField(max_length=500)
    primary_category = models.CharField(max_length=255, blank=True)
    brand = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50, blank=True)
    main_image_url = models.URLField(max_length=1000, blank=True)
    url = models.URLField(max_length=1000, blank=True)
    
    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'daraz_item_id'], name='unique_store_product')
        ]

    def __str__(self):
        return self.name

class Sku(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='skus')
    daraz_sku_id = models.CharField(max_length=255, blank=True)
    seller_sku = models.CharField(max_length=255)
    shop_sku = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=500, blank=True)
    variation = models.JSONField(default=dict)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    special_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    image_url = models.URLField(max_length=1000, blank=True)
    
    package_weight = models.CharField(max_length=50, blank=True)
    package_length = models.CharField(max_length=50, blank=True)
    package_width = models.CharField(max_length=50, blank=True)
    package_height = models.CharField(max_length=50, blank=True)

    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'seller_sku'], name='unique_store_sku')
        ]

    def __str__(self):
        return self.seller_sku

class SkuCost(models.Model):
    class Source(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        CSV = 'csv', 'CSV Import'
        API = 'api', 'API'

    sku = models.ForeignKey(Sku, on_delete=models.CASCADE, related_name='costs')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    packaging_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_from = models.DateTimeField()
    note = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_from']
        indexes = [
            models.Index(fields=['sku', '-effective_from']),
        ]

    def __str__(self):
        return f"{self.sku.seller_sku} Cost @ {self.effective_from}"
