from celery import shared_task
from django.utils import timezone
import datetime

@shared_task
def purge_old_data():
    """
    Purge ApiCallLog > 30 days, LabelJobs > 7 days, Soft-deleted Stores > 90 days.
    """
    pass # In a real implementation this would query those models and delete()
