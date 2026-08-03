from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import CursorPagination
from django.db.models import Sum, Count, Q, F
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.utils import timezone

from .models import Order, OrderItem
from .serializers import OrderListSerializer, OrderDetailSerializer
from apps.core.tenancy import IsStoreOwner

class OrderCursorPagination(CursorPagination):
    page_size = 50
    ordering = '-created_at_daraz'

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsStoreOwner]
    pagination_class = OrderCursorPagination

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.filter(store__owner=user).select_related('customer').prefetch_related('items__sku')
        
        # Filters
        store_id = self.request.query_params.get('store_id')
        if store_id:
            qs = qs.filter(store_id=store_id)
            
        status_bucket = self.request.query_params.get('status')
        if status_bucket and status_bucket != 'All Orders':
            qs = qs.filter(status=status_bucket)
            
        date_from = self.request.query_params.get('date_from')
        if date_from:
            qs = qs.filter(created_at_daraz__gte=parse_datetime(date_from))
            
        date_to = self.request.query_params.get('date_to')
        if date_to:
            qs = qs.filter(created_at_daraz__lte=parse_datetime(date_to))
            
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(order_number__icontains=search) |
                Q(customer__name__icontains=search) |
                Q(customer__phone__icontains=search) |
                Q(items__sku_string__icontains=search) |
                Q(items__name__icontains=search) |
                Q(items__tracking_code__icontains=search)
            ).distinct()
            
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderListSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = self.get_queryset()
        
        # Current period vs Previous period
        # Assuming period is defined by date_from and date_to
        # If no dates, we just return totals for all time.
        # But let's build the aggregations.
        
        # We need sum of gross (price), sum of profit, count of orders, etc.
        agg = qs.aggregate(
            gross_order_value=Sum('price'),
            orders_count=Count('id'),
            returns_count=Count('id', filter=Q(status='Return / Refund')),
            delivered_count=Count('id', filter=Q(status='Delivered')),
            cancellation_count=Count('id', filter=Q(status='Cancellation')),
            pending_rts=Count('id', filter=Q(status='To Ship')),
        )
        
        # Calculate Net Profit via OrderItems
        # We aggregate profit_amount across all items belonging to these orders
        profit_agg = OrderItem.objects.filter(order__in=qs).aggregate(
            net_profit=Sum('profit_amount')
        )
        net_profit = profit_agg['net_profit'] or 0.0
        
        gross = agg['gross_order_value'] or 0.0
        orders_count = agg['orders_count'] or 0
        
        average_order_value = (gross / orders_count) if orders_count else 0
        net_margin_pct = (net_profit / float(gross) * 100) if gross else 0
        
        # Todays Sales
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_agg = qs.filter(created_at_daraz__gte=today_start).aggregate(sales=Sum('price'))
        
        return Response({
            "gross_order_value": float(gross),
            "orders_count": orders_count,
            "net_profit": float(net_profit),
            "net_margin_pct": float(net_margin_pct),
            "pending_rts": agg['pending_rts'],
            "returns_count": agg['returns_count'],
            "delivered_count": agg['delivered_count'],
            "cancellation_count": agg['cancellation_count'],
            "average_order_value": float(average_order_value),
            "todays_sales": float(today_agg['sales'] or 0),
            # Mock deltas and sparklines for now, a full implementation would run grouped queries
            "deltas": {
                "gross_order_value": 15.2,
                "orders_count": -5.0,
                "net_profit": 12.1
            },
            "sparklines": {
                "gross": [10, 15, 12, 20, 18, 25, 22],
                "orders": [5, 7, 6, 9, 8, 12, 10]
            }
        })

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        qs = self.get_queryset()
        
        # Status breakdown
        status_counts = qs.values('status').annotate(count=Count('id')).order_by('-count')
        
        # Top Cities
        top_cities = qs.values('customer__city').annotate(count=Count('id')).exclude(customer__city='').order_by('-count')[:5]
        
        # Mock Orders Over Time
        # Requires TruncDate which we can do simply here
        from django.db.models.functions import TruncDate
        orders_over_time = qs.annotate(date=TruncDate('created_at_daraz')).values('date').annotate(count=Count('id')).order_by('date')
        
        return Response({
            "status_breakdown": list(status_counts),
            "top_cities": [{"city": item['customer__city'], "count": item['count']} for item in top_cities],
            "orders_over_time": [{"date": str(item['date']), "count": item['count']} for item in orders_over_time]
        })

    @action(detail=False, methods=['get'], url_path='needs-attention')
    def needs_attention(self, request):
        qs = self.get_queryset()
        # Orders missing finance (Delivered but no finance)
        # OR items missing cost
        # We can just return a custom list
        attention_qs = qs.filter(
            Q(status='Delivered', finance_transactions__isnull=True) |
            Q(items__profit_confidence='INCOMPLETE')
        ).distinct()[:20]
        
        return Response(OrderListSerializer(attention_qs, many=True).data)

    @action(detail=False, methods=['post'])
    def export(self, request):
        from .tasks import export_orders_csv
        store_id = request.data.get('store_id') or request.query_params.get('store_id')
        if not store_id:
            # Can export across all stores, but let's grab the first one for the task
            store = Store.objects.filter(owner=request.user).first()
            if not store:
                return Response({"error": "No stores connected."}, status=status.HTTP_400_BAD_REQUEST)
            store_id = store.id
            
        export_orders_csv.delay(store_id, request.query_params.dict(), request.user.email)
        return Response({"status": "queued", "message": "You will receive an email when the export is ready."})
