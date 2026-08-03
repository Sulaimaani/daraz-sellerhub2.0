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
}

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return "Celery is working!"
