from rest_framework import serializers
from .models import OnboardingState

class OnboardingStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingState
        fields = ["current_step", "updated_at"]
        read_only_fields = fields
