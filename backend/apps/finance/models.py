from django.db import models
from apps.stores.models import Store
from apps.orders.models import Order, OrderItem

class FinanceTransaction(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='finance_transactions')
    transaction_number = models.CharField(max_length=255) # Hash if Daraz gives none
    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='finance_transactions')
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='finance_transactions')
    
    transaction_type = models.CharField(max_length=100)
    fee_name = models.CharField(max_length=255)
    statement_id = models.CharField(max_length=100, blank=True) # Usually statement_number
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, blank=True)
    vat_in_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    wht_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    transaction_date = models.DateTimeField(null=True, blank=True)
    paid_status = models.CharField(max_length=100, blank=True)
    payment_ref_id = models.CharField(max_length=255, blank=True)
    
    details = models.JSONField(default=dict)
    raw_json = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'transaction_number'], name='unique_store_transaction')
        ]
        indexes = [
            models.Index(fields=['store', 'transaction_date']),
            models.Index(fields=['store', 'order']),
            models.Index(fields=['store', 'transaction_type']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.fee_name} ({self.amount})"

class FinanceStatement(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='finance_statements')
    statement_number = models.CharField(max_length=255)
    
    period_start = models.DateTimeField(null=True, blank=True)
    period_end = models.DateTimeField(null=True, blank=True)
    
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    paid_status = models.CharField(max_length=100, blank=True)
    payout_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payout_date = models.DateTimeField(null=True, blank=True)

    raw_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'statement_number'], name='unique_store_statement')
        ]
        indexes = [
            models.Index(fields=['store', '-period_end']),
        ]

    def __str__(self):
        return self.statement_number
