from rest_framework import serializers
from .models import Store, SyncJob, SyncWindow

class StoreSerializer(serializers.ModelSerializer):
    sync_progress_pct = serializers.SerializerMethodField()
    sync_status = serializers.SerializerMethodField()
    sync_counters = serializers.SerializerMethodField()
    has_120_day_history = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            "id", "name", "short_code", "seller_email", "country", "currency",
            "status", "connected_at", "disconnected_at", "last_sync_at",
            "sync_progress_pct", "sync_status", "sync_counters", "has_120_day_history"
        ]
        read_only_fields = fields

    def get_latest_job(self, obj):
        if not hasattr(self, "_latest_jobs"):
            self._latest_jobs = {}
        if obj.id not in self._latest_jobs:
            self._latest_jobs[obj.id] = obj.sync_jobs.order_by("-created_at").first()
        return self._latest_jobs[obj.id]

    def get_sync_progress_pct(self, obj):
        job = self.get_latest_job(obj)
        return job.progress_pct if job else 0
        
    def get_sync_status(self, obj):
        job = self.get_latest_job(obj)
        return job.status if job else None
        
    def get_sync_counters(self, obj):
        job = self.get_latest_job(obj)
        return job.counters if job else {}
        
    def get_has_120_day_history(self, obj):
        job = self.get_latest_job(obj)
        return job is not None and job.status == SyncJob.Status.DONE

class StoreRenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["name"]


class SyncWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncWindow
        fields = ["id", "date_from", "date_to", "status", "attempts", "last_error", "records_imported"]


class SyncJobSerializer(serializers.ModelSerializer):
    windows = SyncWindowSerializer(many=True, read_only=True)
    
    class Meta:
        model = SyncJob
        fields = [
            "id", "kind", "status", "total_windows", "completed_windows", 
            "progress_pct", "started_at", "finished_at", "error", "counters",
            "windows"
        ]
