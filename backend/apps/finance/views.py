from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FinanceAudit, FinanceIssue
from .serializers import FinanceAuditSerializer, FinanceIssueSerializer
from .tasks import run_finance_audit, export_finance_audit
from django.core.cache import cache

class FinanceAuditViewSet(viewsets.ModelViewSet):
    queryset = FinanceAudit.objects.all().order_by('-run_at')
    serializer_class = FinanceAuditSerializer
    
    def create(self, request, *args, **kwargs):
        store_id = request.data.get('store')
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')
        
        lock_key = f"audit_lock_{store_id}"
        if cache.get(lock_key):
            return Response({"error": "An audit is already running for this store."}, status=status.HTTP_409_CONFLICT)
            
        # Create audit
        audit = FinanceAudit.objects.create(
            store_id=store_id,
            period_start=period_start,
            period_end=period_end,
            status='queued'
        )
        
        # Lock for 5 mins to prevent spam
        cache.set(lock_key, True, timeout=300)
        
        # Queue task
        run_finance_audit.delay(audit.id)
        
        serializer = self.get_serializer(audit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        # Drill down orders
        audit = self.get_object()
        # Simple mock for pagination
        return Response({"orders": []})

    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        audit = self.get_object()
        export_format = request.data.get('format', 'csv')
        export_finance_audit.delay(audit.id, export_format)
        return Response({"status": "Export queued"})

class FinanceIssueViewSet(viewsets.ModelViewSet):
    queryset = FinanceIssue.objects.all()
    serializer_class = FinanceIssueSerializer
    
    def update(self, request, *args, **kwargs):
        issue = self.get_object()
        issue.resolved = request.data.get('resolved', issue.resolved)
        issue.resolved_note = request.data.get('resolved_note', issue.resolved_note)
        issue.save()
        return Response(self.get_serializer(issue).data)
