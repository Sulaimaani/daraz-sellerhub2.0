from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReturnPackageViewSet, ReturnClaimViewSet, PackageInspectionViewSet

router = DefaultRouter()
router.register(r'packages', ReturnPackageViewSet, basename='return-package')
router.register(r'claims', ReturnClaimViewSet, basename='return-claim')
router.register(r'inspections', PackageInspectionViewSet, basename='package-inspection')

urlpatterns = [
    path('', include(router.urls)),
]
