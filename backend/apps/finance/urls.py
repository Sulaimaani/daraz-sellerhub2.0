from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinanceAuditViewSet, FinanceIssueViewSet

router = DefaultRouter()
router.register(r'audits', FinanceAuditViewSet, basename='audit')
router.register(r'issues', FinanceIssueViewSet, basename='issue')

urlpatterns = [
    path('', include(router.urls)),
]
