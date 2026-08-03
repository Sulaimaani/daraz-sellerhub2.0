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


@shared_task
def process_sync_windows(job_id):
    try:
        job = SyncJob.objects.get(id=job_id)
    except SyncJob.DoesNotExist:
        return
        
    if job.status in [SyncJob.Status.DONE, SyncJob.Status.FAILED, SyncJob.Status.CANCELLED]:
        return

    windows = job.windows.filter(status__in=[SyncWindow.Status.PENDING, SyncWindow.Status.FAILED])
    
    client = DarazClient(store=job.store)
    
    for window in windows:
        window.status = SyncWindow.Status.RUNNING
        window.attempts += 1
        window.save(update_fields=["status", "attempts"])
        
        try:
            # We call the mock generators to simulate importing records
            # Since DARAZ_MOCK is set, client will route to mock responses
            
            # 1. Orders
            orders_res = client.call("/orders/get", {"created_before": window.date_to.isoformat(), "created_after": window.date_from.isoformat()})
            # 2. Finance
            client.call("/finance/transaction/detail/get", {"start_time": window.date_from.isoformat(), "end_time": window.date_to.isoformat()})
            
            # Count them up
            orders_count = len(orders_res.get("data", {}).get("orders", []))
            
            window.records_imported = orders_count
            window.status = SyncWindow.Status.COMPLETED
            window.save()
            
            # Update job counters
            job.completed_windows += 1
            counters = job.counters or {"orders": 0, "finance": 0, "returns": 0, "profit": 0}
            counters["orders"] = counters.get("orders", 0) + orders_count
            # Rough math for fake counters
            counters["finance"] = counters.get("finance", 0) + orders_count
            job.counters = counters
            job.save(update_fields=["completed_windows", "counters"])
            
        except Exception as e:
            window.status = SyncWindow.Status.FAILED
            window.last_error = str(e)
            window.save()
            # Stop processing this job for now to allow retry logic / resumability to take over
            job.status = SyncJob.Status.FAILED
            job.error = f"Window {window.id} failed: {e}"
            job.save(update_fields=["status", "error"])
            return
            
    # If we made it here, check if all windows are done
    if not job.windows.exclude(status=SyncWindow.Status.COMPLETED).exists():
        job.status = SyncJob.Status.DONE
        job.finished_at = timezone.now()
        job.save(update_fields=["status", "finished_at"])
        
        # update store last_sync_at
        job.store.last_sync_at = timezone.now()
        job.store.save(update_fields=["last_sync_at"])

@shared_task
def purge_api_call_logs():
    from apps.stores.models import ApiCallLog
    cutoff = timezone.now() - timedelta(days=30)
    deleted, _ = ApiCallLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Purged {deleted} ApiCallLog entries older than 30 days.")

