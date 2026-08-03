from celery import shared_task
from apps.products.models import Sku
from apps.orders.models import OrderItem
from apps.finance.profit import compute_order_item_profit

@shared_task
def recompute_profit_for_sku(sku_id):
    """
    Called when a SkuCost is modified. Recomputes the profit for all OrderItems associated with this SKU.
    """
    sku = Sku.objects.get(id=sku_id)
    items = OrderItem.objects.filter(sku_string=sku.seller_sku, order__store=sku.store)
    
    for item in items:
        compute_order_item_profit(item)
