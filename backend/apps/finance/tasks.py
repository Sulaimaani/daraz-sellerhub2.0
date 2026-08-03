from celery import shared_task
from .audit_engine import run_audit
import logging

logger = logging.getLogger(__name__)

@shared_task
def run_finance_audit(audit_id):
    try:
        run_audit(audit_id)
    except Exception as e:
        logger.error(f"Finance audit failed: {e}")
        from .models import FinanceAudit
        try:
            audit = FinanceAudit.objects.get(id=audit_id)
            audit.status = 'failed'
            audit.save(update_fields=['status'])
        except:
            pass

@shared_task
def export_finance_audit(audit_id, format='csv'):
    # Mocking export to Spaces
    pass
