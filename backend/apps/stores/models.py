from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.crypto import EncryptedTextField
from apps.core.models import TimeStampedModel


class StoreManager(models.Manager):
    def get_queryset(self):
        # We only filter out soft-deleted stores here if needed,
        # but the spec says "soft-delete on disconnect - never hard delete, so SKU settings survive"
        # Disconnected stores should still be retrievable but perhaps excluded from syncs.
        return super().get_queryset()


class Store(TimeStampedModel):
    class Status(models.TextChoices):
        CONNECTED = "connected", _("Connected")
        DISCONNECTED = "disconnected", _("Disconnected")
        NEEDS_RECONNECT = "needs_reconnect", _("Needs Reconnect")
        ERROR = "error", _("Error")

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="stores")
    daraz_seller_id = models.CharField(max_length=255, db_index=True)
    
    name = models.CharField(max_length=255)
    short_code = models.CharField(max_length=50, blank=True)
    seller_email = models.EmailField(blank=True)
    country = models.CharField(max_length=2, default="PK")
    currency = models.CharField(max_length=3, default="PKR")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONNECTED)
    
    connected_at = models.DateTimeField(null=True, blank=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    raw_seller_json = models.JSONField(default=dict, blank=True)
    
    objects = StoreManager()

    class Meta:
        # One daraz_seller_id per user (the system shouldn't have duplicate connected sellers for the same user)
        # Actually daraz_seller_id should be unique across the whole DB ideally, but the spec says "unique per owner"
        # Wait, spec: "Reconnecting the SAME daraz_seller_id must reuse the existing Store row... Connecting a daraz_seller_id already owned by a DIFFERENT user must fail with a clear 409."
        # This implies daraz_seller_id is globally unique in our system for active stores. We will enforce this in views.
        constraints = [
            models.UniqueConstraint(fields=["owner", "daraz_seller_id"], name="unique_store_per_owner")
        ]

    def __str__(self):
        return f"{self.name} ({self.country})"


class OAuthToken(TimeStampedModel):
    store = models.OneToOneField(Store, on_delete=models.CASCADE, related_name="oauth_token")
    access_token = EncryptedTextField()
    refresh_token = EncryptedTextField()
    
    access_expires_at = models.DateTimeField()
    refresh_expires_at = models.DateTimeField()
    
    scope = models.CharField(max_length=255, blank=True)
    last_refreshed_at = models.DateTimeField(auto_now_add=True)
    refresh_failures = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Token for {self.store}"


class SyncJob(TimeStampedModel):
    class Kind(models.TextChoices):
        HISTORY = "history", _("History")
        ORDERS = "orders", _("Orders")
        FINANCE = "finance", _("Finance")
        RETURNS = "returns", _("Returns")

    class Status(models.TextChoices):
        QUEUED = "queued", _("Queued")
        RUNNING = "running", _("Running")
        DONE = "done", _("Done")
        FAILED = "failed", _("Failed")
        CANCELLED = "cancelled", _("Cancelled")

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="sync_jobs")
    kind = models.CharField(max_length=20, choices=Kind.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    
    total_windows = models.PositiveIntegerField(default=0)
    completed_windows = models.PositiveIntegerField(default=0)
    
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)
    counters = models.JSONField(default=dict, blank=True)

    @property
    def progress_pct(self):
        if self.total_windows == 0:
            return 0
        return int((self.completed_windows / self.total_windows) * 100)

    def __str__(self):
        return f"{self.get_kind_display()} Job for {self.store}"


class SyncWindow(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        RUNNING = "running", _("Running")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    sync_job = models.ForeignKey(SyncJob, on_delete=models.CASCADE, related_name="windows")
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    records_imported = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sync_job", "date_from", "date_to"], name="unique_sync_window")
        ]

    def __str__(self):
        return f"Window {self.date_from} - {self.date_to} ({self.status})"


class ApiCallLog(TimeStampedModel):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, related_name="api_logs")
    api_path = models.CharField(max_length=255)
    http_status = models.IntegerField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    
    request_params = models.JSONField(default=dict, blank=True)
    response_snippet = models.TextField(blank=True)
    error_code = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["store", "created_at"]),
            models.Index(fields=["api_path", "created_at"]),
        ]

    def __str__(self):
        return f"{self.api_path} ({self.http_status})"


class OAuthState(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, unique=True)
    consumed_at = models.DateTimeField(null=True, blank=True)
    redirect_after = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return f"State for {self.user}"
