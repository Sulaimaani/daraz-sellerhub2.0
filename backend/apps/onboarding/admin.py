from django.contrib import admin
from .models import OnboardingState

@admin.register(OnboardingState)
class OnboardingStateAdmin(admin.ModelAdmin):
    list_display = ("user", "current_step", "updated_at")
    list_filter = ("current_step",)
