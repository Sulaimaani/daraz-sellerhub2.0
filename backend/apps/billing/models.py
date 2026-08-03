from django.db import models
from apps.accounts.models import User
from django.conf import settings
from django.utils import timezone
import datetime

class SubscriptionPlan(models.Model):
    # Plans (Starter / Growth / Business) differing by connected store count, label volume per month, and history retention. Define the limits in settings so they can be tuned without a migration.
    
    name = models.CharField(max_length=100) # Starter, Growth, Business
    code = models.CharField(max_length=50, unique=True)
    price_pkr = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    
    def get_limits(self):
        # Fallback if not defined in settings
        limits = getattr(settings, 'BILLING_PLAN_LIMITS', {
            'starter': {'stores': 1, 'labels': 500, 'history_days': 120},
            'growth': {'stores': 3, 'labels': 5000, 'history_days': 365},
            'business': {'stores': 10, 'labels': 50000, 'history_days': 1095},
        })
        return limits.get(self.code, limits['starter'])

    def __str__(self):
        return self.name

class StoreSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=50, default='trialing') # trialing, active, past_due, canceled
    
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        now = timezone.now()
        if self.status == 'trialing' and self.trial_end and now <= self.trial_end:
            return True
        if self.status == 'active' and self.current_period_end and now <= self.current_period_end:
            return True
        return False
        
    def __str__(self):
        return f"{self.user.email} - {self.plan.name if self.plan else 'No Plan'}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_pct = models.DecimalField(max_digits=5, decimal_places=2)
    expiry = models.DateTimeField(null=True, blank=True)
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)

    def is_valid(self):
        if self.expiry and timezone.now() > self.expiry:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True

class Invoice(models.Model):
    subscription = models.ForeignKey(StoreSubscription, on_delete=models.CASCADE, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending') # pending, paid, void
    payment_method = models.CharField(max_length=50, default='manual_transfer')
    
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    pdf_url = models.URLField(blank=True)
    
    def __str__(self):
        return f"Invoice {self.id} - {self.status}"
