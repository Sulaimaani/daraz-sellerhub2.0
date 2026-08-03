import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("darazsaas")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from celery.schedules import crontab

app.conf.beat_schedule = {
    "refresh-expiring-tokens-hourly": {
        "task": "apps.stores.tasks.refresh_expiring_tokens",
        "schedule": crontab(minute=0),
    },
    "purge-api-call-logs-daily": {
        "task": "apps.stores.tasks.purge_api_call_logs",
        "schedule": crontab(hour=2, minute=0),
    },
    "purge-old-data-daily": {
        "task": "apps.core.tasks.purge_old_data",
        "schedule": crontab(hour=3, minute=0),
    },
    "sync-recent-orders-half-hourly": {
        "task": "apps.stores.tasks.sync_recent_orders",
        "schedule": crontab(minute='*/30'),
    },
    "sync-finance-daily": {
        "task": "apps.stores.tasks.sync_finance",
        "schedule": crontab(hour=4, minute=0),
    },
    "sync-returns-daily": {
        "task": "apps.stores.tasks.sync_returns",
        "schedule": crontab(hour=5, minute=0),
    },
    "sync-products-daily": {
        "task": "apps.stores.tasks.sync_products",
        "schedule": crontab(hour=6, minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return "Celery is working!"
