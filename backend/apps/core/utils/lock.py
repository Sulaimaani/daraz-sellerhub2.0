from django.core.cache import cache
from contextlib import contextmanager

class SyncLockError(Exception):
    pass

@contextmanager
def store_sync_lock(store_id: int, lock_type: str, timeout: int = 3600):
    """
    Ensures that only one sync of `lock_type` (e.g., 'orders', 'products', 'finance')
    runs per store at any given time.
    """
    lock_id = f"store_{store_id}_sync_{lock_type}_lock"
    # cache.add returns True if the key was added, False if it already existed
    acquired = cache.add(lock_id, "locked", timeout)
    if not acquired:
        raise SyncLockError(f"Could not acquire lock for {lock_id}. Sync is already running.")
    try:
        yield
    finally:
        cache.delete(lock_id)
