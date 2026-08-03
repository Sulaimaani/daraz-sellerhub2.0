from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel

class OnboardingState(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="onboarding_state")
    current_step = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Onboarding State for {self.user} (Step {self.current_step})"
