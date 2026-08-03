import redis
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from celery import current_app

def readyz(request):
    """Shallow check for App Platform routing."""
    return JsonResponse({"status": "ok"}, status=200)

def healthz(request):
    db_ok = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row[0] == 1:
                db_ok = True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("DB health check failed: %s", e)

    redis_ok = False
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        if r.ping():
            redis_ok = True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Redis health check failed: %s", e)

    celery_ok = False
    try:
        # Check celery worker heartbeat
        inspector = current_app.control.inspect()
        stats = inspector.stats()
        if stats:
            celery_ok = True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Celery health check failed: %s", e)

    status_code = 200 if db_ok and redis_ok and celery_ok else 500

    return JsonResponse(
        {
            "status": "ok" if status_code == 200 else "error",
            "db": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
            "celery": "ok" if celery_ok else "error",
        },
        status=status_code,
    )
