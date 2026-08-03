from celery import shared_task
from django.utils import timezone
from apps.stores.models import Store
from apps.orders.models import OrderItem
from apps.finance.profit import compute_order_item_profit
import logging

logger = logging.getLogger(__name__)

@shared_task
def recompute_store_profit(store_id):
    """
    Re-runs the profit engine on all items for a store.
    Called when SkuCost changes or a finance sync completes.
    """
    try:
        store = Store.objects.get(id=store_id)
        # Process in chunks to avoid blowing up memory if the store has 100k items
        # Use iterator or paginated slicing
        items = OrderItem.objects.filter(store=store).prefetch_related('finance_transactions', 'sku__costs')
        
        count = 0
        for item in items.iterator(chunk_size=2000):
            compute_order_item_profit(item)
            count += 1
            
        logger.info(f"Recomputed profit for {count} items in Store {store_id}")
    except Store.DoesNotExist:
        pass


@shared_task
def export_orders_csv(store_id, filter_params, email_to):
    """
    Generates a CSV of orders based on the filter params.
    In a real app, this uploads to DO Spaces and emails a signed link.
    For this phase, we mock the generation and Space upload.
    """
    import csv
    import tempfile
    import os
    
    # Mocking export
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
        writer = csv.writer(tmp)
        writer.writerow(["Order Number", "Date", "Status", "Total"])
        writer.writerow(["MOCK-123", "2026-08-01", "Delivered", "100.00"])
        tmp_path = tmp.name
        
    logger.info(f"Exported CSV for Store {store_id} to {tmp_path}")
    # TODO: Boto3 upload to DigitalOcean Spaces
    # s3_client.upload_file(tmp_path, settings.AWS_STORAGE_BUCKET_NAME, object_name)
    # url = s3_client.generate_presigned_url('get_object', Params={'Bucket': ..., 'Key': ...}, ExpiresIn=3600)
    # send_email(email_to, url)
    
    os.remove(tmp_path)
