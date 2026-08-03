from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SkuViewSet, SkuCostViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'skus', SkuViewSet, basename='sku')
router.register(r'costs', SkuCostViewSet, basename='sku-cost')

urlpatterns = [
    path('', include(router.urls)),
]
