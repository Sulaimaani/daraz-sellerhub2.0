import csv
import io
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Product, Sku, SkuCost
from .serializers import ProductSerializer, SkuSerializer, SkuCostSerializer
from .tasks import recompute_profit_for_sku

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('skus').all()
    serializer_class = ProductSerializer

class SkuViewSet(viewsets.ModelViewSet):
    queryset = Sku.objects.prefetch_related('costs').all()
    serializer_class = SkuSerializer

class SkuCostViewSet(viewsets.ModelViewSet):
    queryset = SkuCost.objects.all()
    serializer_class = SkuCostSerializer
    
    def perform_create(self, serializer):
        cost = serializer.save()
        recompute_profit_for_sku.delay(cost.sku_id)

    def perform_update(self, serializer):
        cost = serializer.save()
        recompute_profit_for_sku.delay(cost.sku_id)

    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        accepted = 0
        rejected = []
        
        costs_to_create = []
        sku_ids_to_recompute = set()
        
        for row_idx, row in enumerate(reader, start=2):
            seller_sku = row.get('seller_sku')
            try:
                sku = Sku.objects.get(seller_sku=seller_sku, store_id=request.data.get('store_id'))
                costs_to_create.append(
                    SkuCost(
                        sku=sku,
                        cost_price=row.get('cost_price', 0) or 0,
                        packaging_cost=row.get('packaging_cost', 0) or 0,
                        other_cost=row.get('other_cost', 0) or 0,
                        effective_from=timezone.now(),
                        source=SkuCost.Source.CSV
                    )
                )
                sku_ids_to_recompute.add(sku.id)
                accepted += 1
            except Sku.DoesNotExist:
                rejected.append({"row": row_idx, "reason": f"SKU {seller_sku} not found"})
        
        # Dry run logic: if this is a preview, don't commit
        if request.data.get('preview') == 'true':
            return Response({
                "accepted": accepted,
                "rejected": rejected
            })
            
        # If not preview and no rejections, commit
        if rejected and request.data.get('force') != 'true':
            return Response({"error": "File contains rejected rows. Fix them or force.", "rejected": rejected}, status=status.HTTP_400_BAD_REQUEST)
            
        SkuCost.objects.bulk_create(costs_to_create)
        
        for sid in sku_ids_to_recompute:
            recompute_profit_for_sku.delay(sid)
            
        return Response({"status": "Imported", "accepted": accepted})
