from rest_framework import serializers
from .models import Product, Sku, SkuCost

class SkuCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkuCost
        fields = '__all__'

class SkuSerializer(serializers.ModelSerializer):
    costs = SkuCostSerializer(many=True, read_only=True)
    
    class Meta:
        model = Sku
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    skus = SkuSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
