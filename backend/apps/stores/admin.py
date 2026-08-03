from django.contrib import admin
from .models import Store, OAuthToken, SyncJob, SyncWindow, ApiCallLog, OAuthState


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "daraz_seller_id", "owner", "status", "connected_at")
    list_filter = ("status", "country")
    search_fields = ("name", "daraz_seller_id", "seller_email")


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ("store", "access_expires_at", "refresh_expires_at", "last_refreshed_at")
    # Completely exclude token fields from the admin form to ensure they are never rendered in plaintext
    exclude = ("access_token", "refresh_token")
    readonly_fields = ("store", "access_expires_at", "refresh_expires_at", "scope", "last_refreshed_at", "refresh_failures")


class SyncWindowInline(admin.TabularInline):
    model = SyncWindow
    extra = 0
    readonly_fields = ("date_from", "date_to", "status", "attempts", "last_error", "records_imported")


@admin.register(SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = ("store", "kind", "status", "progress_pct", "started_at", "finished_at")
    list_filter = ("kind", "status")
    search_fields = ("store__name", "store__daraz_seller_id")
    inlines = [SyncWindowInline]


@admin.register(ApiCallLog)
class ApiCallLogAdmin(admin.ModelAdmin):
    list_display = ("api_path", "store", "http_status", "duration_ms", "created_at")
    list_filter = ("http_status",)
    search_fields = ("api_path", "error_code", "store__name")
    readonly_fields = ("store", "api_path", "http_status", "duration_ms", "request_params", "response_snippet", "error_code", "created_at")

@admin.register(OAuthState)
class OAuthStateAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "consumed_at")
