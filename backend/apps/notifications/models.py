from django.db import models
from apps.accounts.models import User

class NotificationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_prefs')
    
    # claim_deadline_24h, claim_deadline_missed, package_arrived, etc.
    trigger_name = models.CharField(max_length=100)
    
    in_app = models.BooleanField(default=True)
    email = models.BooleanField(default=True)
    sms = models.BooleanField(default=False)
    whatsapp = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'trigger_name'], name='unique_user_trigger')
        ]
        
    def __str__(self):
        return f"{self.user.email} - {self.trigger_name}"

class NotificationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trigger_name = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100) # e.g. ReturnPackage ID or Claim ID
    
    sent_at = models.DateTimeField(auto_now_add=True)
    channel = models.CharField(max_length=50) # email, in_app
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'trigger_name', 'entity_id', 'channel'], name='unique_dispatch')
        ]
