from rest_framework import serializers
from .models import Order, OrderItem, Customer, Shipment
from apps.finance.models import FinanceTransaction

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'city', 'address_line']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'name', 'sku_string', 'variation', 'status', 'item_price',
            'profit_amount', 'profit_confidence', 'profit_computed_at', 'image_url' # Assuming image_url on Sku... wait Sku is FK.
        ]
        
    image_url = serializers.CharField(source='sku.image_url', read_only=True)

class FinanceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceTransaction
        fields = ['transaction_type', 'fee_name', 'amount', 'transaction_date']

class OrderItemDetailSerializer(OrderItemSerializer):
    finance_transactions = FinanceTransactionSerializer(many=True, read_only=True)
    sku_cost = serializers.SerializerMethodField()
    
    class Meta(OrderItemSerializer.Meta):
        fields = OrderItemSerializer.Meta.fields + ['finance_transactions', 'sku_cost']
        
    def get_sku_cost(self, obj):
        # We look up the cost applied during the order time
        if not obj.sku:
            return None
        order_date = obj.created_at_daraz or obj.created_at
        cost_row = obj.sku.costs.filter(effective_from__lte=order_date).order_by('-effective_from').first()
        if cost_row:
            return {
                "unit_cost": float(cost_row.cost_price + cost_row.packaging_cost + cost_row.other_cost),
                "effective_from": cost_row.effective_from
            }
        return None

class OrderListSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    masked_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_method', 'price', 
            'items_count', 'created_at_daraz', 'customer', 'items', 'masked_phone'
        ]
        
    def get_masked_phone(self, obj):
        if not obj.customer or not obj.customer.phone:
            return ""
        phone = obj.customer.phone
        if len(phone) > 4:
            return "*" * (len(phone) - 4) + phone[-4:]
        return phone

class OrderDetailSerializer(OrderListSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    
    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + ['shipping_fee', 'voucher', 'tax_amount', 'raw_json']
