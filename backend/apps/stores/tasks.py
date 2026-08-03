from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from apps.stores.models import Store, OAuthToken, SyncJob, SyncWindow
from apps.core.daraz.client import DarazClient, DarazAuthError, DarazApiError

logger = logging.getLogger(__name__)

@shared_task
def refresh_expiring_tokens():
    # Refresh anything expiring within 24h
    expiring_cutoff = timezone.now() + timedelta(hours=24)
    tokens = OAuthToken.objects.filter(access_expires_at__lt=expiring_cutoff, store__status=Store.Status.CONNECTED)
    
    for token in tokens:
        client = DarazClient(store=token.store)
        try:
            res = client.refresh_token(token.refresh_token)
            
            # success
            access_token = res.get("access_token")
            if access_token:
                token.access_token = access_token
                token.refresh_token = res.get("refresh_token", token.refresh_token)
                token.access_expires_at = timezone.now() + timedelta(seconds=int(res.get("expires_in", 2592000)))
                token.refresh_expires_at = timezone.now() + timedelta(seconds=int(res.get("refresh_expires_in", 15552000)))
                token.refresh_failures = 0
                token.last_refreshed_at = timezone.now()
                token.save()
        except Exception as e:
            logger.error(f"Failed to refresh token for store {token.store.id}: {e}")
            token.refresh_failures += 1
            token.save(update_fields=["refresh_failures"])
            
            # after N failures, set status to needs_reconnect
            if token.refresh_failures >= 3:
                token.store.status = Store.Status.NEEDS_RECONNECT
                token.store.save(update_fields=["status"])


@shared_task(bind=True)
def start_history_import(self, store_id):
    """
    Creates the SyncJob and its 7-day SyncWindows across 120 days.
    """
    store = Store.objects.get(id=store_id)
    
    # Create the SyncJob if not resumed
    job = SyncJob.objects.create(
        store=store,
        kind=SyncJob.Kind.HISTORY,
        status=SyncJob.Status.RUNNING,
        started_at=timezone.now()
    )
    
    # Chunk 120 days into 7-day windows
    end_date = timezone.now()
    start_date = end_date - timedelta(days=120)
    
    current_start = start_date
    windows_created = 0
    while current_start < end_date:
        current_end = current_start + timedelta(days=7)
        if current_end > end_date:
            current_end = end_date
            
        SyncWindow.objects.get_or_create(
            sync_job=job,
            date_from=current_start,
            date_to=current_end
        )
        current_start = current_end
        windows_created += 1
        
    job.total_windows = windows_created
    job.save(update_fields=["total_windows"])
    
    # Enqueue window processor for this job
    process_sync_windows.delay(job.id)


@shared_task(bind=True, max_retries=3)
def process_sync_windows(self, job_id):
    from apps.core.utils.lock import store_sync_lock, SyncLockError
    from apps.orders.sync import sync_orders_window, sync_finance_window, sync_returns_window, sync_products_window
    
    try:
        job = SyncJob.objects.get(id=job_id)
    except SyncJob.DoesNotExist:
        return
        
    if job.status in [SyncJob.Status.DONE, SyncJob.Status.FAILED, SyncJob.Status.CANCELLED]:
        return

    windows = job.windows.filter(status__in=[SyncWindow.Status.PENDING, SyncWindow.Status.FAILED]).order_by('date_from')
    
    # We acquire a lock for the whole job chunk to prevent overlapping jobs for the same store
    try:
        with store_sync_lock(job.store.id, lock_type="history", timeout=1800): # 30 min lock
            for window in windows:
                window.status = SyncWindow.Status.RUNNING
                window.attempts += 1
                window.save(update_fields=["status", "attempts"])
                
                try:
                    # Sync Products only once per job (e.g. on first window) to populate SKUs for linking
                    if job.completed_windows == 0:
                        sync_products_window(job.store)
                        
                    sync_orders_window(job.store, window.date_from, window.date_to)
                    sync_finance_window(job.store, window.date_from, window.date_to)
                    sync_returns_window(job.store)
                    
                    window.status = SyncWindow.Status.COMPLETED
                    window.save()
                    
                    job.completed_windows += 1
                    job.save(update_fields=["completed_windows"])
                    
                except Exception as e:
                    window.status = SyncWindow.Status.FAILED
                    window.last_error = str(e)
                    window.save()
                    logger.error(f"Sync window {window.id} failed: {e}")
                    # Retry the Celery task itself with exponential backoff (e.g., 60s, 300s, 900s)
                    raise self.retry(exc=e, countdown=60 * (5 ** self.request.retries))
                    
    except SyncLockError as e:
        logger.warning(str(e))
        return
            
    # If we made it here without raising retries, check if all windows are done
    if not job.windows.exclude(status=SyncWindow.Status.COMPLETED).exists():
        job.status = SyncJob.Status.DONE
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at"])
        
        job.store.last_sync_at = timezone.now()
        job.store.save(update_fields=["last_sync_at"])

@shared_task
def sync_recent_orders():
    from apps.core.utils.lock import store_sync_lock, SyncLockError
    from apps.orders.sync import sync_orders_window
    stores = Store.objects.filter(status=Store.Status.CONNECTED)
    for store in stores:
        try:
            with store_sync_lock(store.id, lock_type="recent_orders", timeout=600):
                end_date = timezone.now()
                # 30 min overlap buffer
                start_date = (store.last_sync_at - timedelta(minutes=30)) if store.last_sync_at else end_date - timedelta(days=1)
                sync_orders_window(store, start_date, end_date)
                store.last_sync_at = end_date
                store.save(update_fields=["last_sync_at"])
        except SyncLockError:
            pass

@shared_task
def sync_finance():
    from apps.core.utils.lock import store_sync_lock, SyncLockError
    from apps.orders.sync import sync_finance_window
    stores = Store.objects.filter(status=Store.Status.CONNECTED)
    for store in stores:
        try:
            with store_sync_lock(store.id, lock_type="finance", timeout=600):
                end_date = timezone.now()
                start_date = end_date - timedelta(days=7) # rolling 7 day
                sync_finance_window(store, start_date, end_date)
        except SyncLockError:
            pass

@shared_task
def sync_returns():
    from apps.core.utils.lock import store_sync_lock, SyncLockError
    from apps.orders.sync import sync_returns_window
    stores = Store.objects.filter(status=Store.Status.CONNECTED)
    for store in stores:
        try:
            with store_sync_lock(store.id, lock_type="returns", timeout=600):
                sync_returns_window(store)
        except SyncLockError:
            pass

@shared_task
def sync_products():
    from apps.core.utils.lock import store_sync_lock, SyncLockError
    from apps.orders.sync import sync_products_window
    stores = Store.objects.filter(status=Store.Status.CONNECTED)
    for store in stores:
        try:
            with store_sync_lock(store.id, lock_type="products", timeout=1200):
                sync_products_window(store)
        except SyncLockError:
            pass

@shared_task
def purge_api_call_logs():
    from apps.stores.models import ApiCallLog
    cutoff = timezone.now() - timedelta(days=30)
    deleted, _ = ApiCallLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Purged {deleted} ApiCallLog entries older than 30 days.")

