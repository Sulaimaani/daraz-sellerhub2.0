from django.urls import path
from .views import OnboardingStateView

urlpatterns = [
    path("", OnboardingStateView.as_view(), name="onboarding-state"),
    path("step/", OnboardingStateView.as_view(), name="onboarding-step"),
]
