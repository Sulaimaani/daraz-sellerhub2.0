import json
import secrets
from datetime import timedelta
from urllib.parse import urlencode, urljoin

from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.daraz.client import DarazClient, DarazAuthError, DarazApiError
from apps.core.tenancy import IsStoreOwner
from apps.stores.models import Store, OAuthState, OAuthToken, SyncJob
from apps.stores.serializers import StoreSerializer, StoreRenameSerializer, SyncJobSerializer
from apps.stores.tasks import start_history_import


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsStoreOwner]

    def get_queryset(self):
        return Store.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return StoreRenameSerializer
        return super().get_serializer_class()

    def _generate_auth_url(self, user):
        # 10 minute TTL
        state_val = secrets.token_urlsafe(32)
        OAuthState.objects.create(
            user=user,
            state=state_val,
            # we could also store the target frontend URL to redirect to in redirect_after
        )
        params = {
            "client_id": settings.DARAZ_APP_KEY,
            "redirect_uri": settings.DARAZ_REDIRECT_URI,
            "response_type": "code",
            "state": state_val,
        }
        # In mock mode, we still generate a URL but to a local mock endpoint? Or we just return the real URL structure.
        base_url = "https://api.daraz.pk/oauth/authorize"
        return f"{base_url}?{urlencode(params)}"

    @action(detail=False, methods=["post"])
    def connect(self, request):
        auth_url = self._generate_auth_url(request.user)
        return Response({"authorize_url": auth_url})

    @action(detail=False, methods=["get"])
    def callback(self, request):
        code = request.GET.get("code")
        state_val = request.GET.get("state")
        error_param = request.GET.get("error")
        
        frontend_base = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else "http://localhost:3000"
        onboarding_wizard_url = urljoin(frontend_base, "/onboarding")
        
        def redirect_with_error(err_msg):
            url = f"{onboarding_wizard_url}?error={err_msg}"
            return redirect(url)

        if error_param:
            return redirect_with_error("auth_denied")

        if not code or not state_val:
            return redirect_with_error("invalid_request")

        # Validate state
        try:
            oauth_state = OAuthState.objects.get(state=state_val)
        except OAuthState.DoesNotExist:
            return redirect_with_error("invalid_state")

        # Check consumption and TTL (10 mins)
        if oauth_state.consumed_at:
            return redirect_with_error("state_already_consumed")
            
        if timezone.now() > oauth_state.created_at + timedelta(minutes=10):
            return redirect_with_error("state_expired")

        # Check user isolation (state issued to A presented by B)
        # Note: OAuth callback might be in a different browser session if user isn't logged in,
        # but since we are relying on cookies, request.user should match.
        if request.user.is_authenticated and oauth_state.user != request.user:
            return redirect_with_error("cross_user_state")
            
        # We process it on behalf of the state user
        user = oauth_state.user
        oauth_state.consumed_at = timezone.now()
        oauth_state.save(update_fields=["consumed_at"])

        client = DarazClient()
        try:
            token_data = client.create_token(code)
            
            # The structure from Daraz: token_data -> access_token, refresh_token, account_id, expires_in, refresh_expires_in
            access_token = token_data.get("access_token")
            if not access_token:
                return redirect_with_error("missing_token")
                
            # Get seller info
            seller_res = client.get_seller(access_token)
            seller_data = seller_res.get("data", {})
            daraz_seller_id = seller_data.get("seller_id", token_data.get("account_id"))
            
            if not daraz_seller_id:
                return redirect_with_error("missing_seller_id")
                
            # Check for conflict
            conflict = Store.objects.filter(daraz_seller_id=daraz_seller_id).exclude(owner=user).exists()
            if conflict:
                return redirect_with_error("store_already_connected_by_other_user")

            with transaction.atomic():
                # Get or create store
                store, created = Store.objects.get_or_create(
                    owner=user,
                    daraz_seller_id=daraz_seller_id,
                    defaults={
                        "name": seller_data.get("name", "Unknown Store"),
                        "short_code": seller_data.get("short_code", ""),
                        "seller_email": seller_data.get("email", ""),
                        "status": Store.Status.CONNECTED,
                        "connected_at": timezone.now(),
                        "raw_seller_json": seller_data,
                    }
                )
                
                if not created:
                    store.status = Store.Status.CONNECTED
                    store.disconnected_at = None
                    store.raw_seller_json = seller_data
                    store.name = seller_data.get("name", store.name)
                    store.save()

                # Update or create Token
                OAuthToken.objects.update_or_create(
                    store=store,
                    defaults={
                        "access_token": access_token,
                        "refresh_token": token_data.get("refresh_token"),
                        "access_expires_at": timezone.now() + timedelta(seconds=int(token_data.get("expires_in", 2592000))),
                        "refresh_expires_at": timezone.now() + timedelta(seconds=int(token_data.get("refresh_expires_in", 15552000))),
                        "refresh_failures": 0,
                        "last_refreshed_at": timezone.now()
                    }
                )

                # Start async sync job if none exists or latest is cancelled/failed
                latest_job = store.sync_jobs.order_by("-created_at").first()
                if not latest_job or latest_job.status in [SyncJob.Status.DONE, SyncJob.Status.FAILED, SyncJob.Status.CANCELLED]:
                    start_history_import.delay(store.id)

            return redirect(f"{onboarding_wizard_url}?step=3")
            
        except Exception as e:
            # We don't want stack trace in URL
            return redirect_with_error("api_error")


    @action(detail=True, methods=["post"])
    def disconnect(self, request, pk=None):
        store = self.get_object()
        store.status = Store.Status.DISCONNECTED
        store.disconnected_at = timezone.now()
        store.save(update_fields=["status", "disconnected_at"])
        
        # Soft-delete: we keep the store, but we can clear the tokens if needed.
        # Actually keeping tokens might be a security risk if disconnected, but spec says "reconnect" later
        # usually involves going through OAuth again anyway.
        if hasattr(store, 'oauth_token'):
            store.oauth_token.delete()
            
        return Response({"status": "disconnected"})

    @action(detail=True, methods=["post"])
    def reconnect(self, request, pk=None):
        store = self.get_object()
        # Same process as connect
        auth_url = self._generate_auth_url(request.user)
        return Response({"authorize_url": auth_url})

    @action(detail=True, methods=["post"], url_path="rebuild-history")
    def rebuild_history(self, request, pk=None):
        store = self.get_object()
        
        # Refuse to start if a job is already running or queued
        active_jobs = store.sync_jobs.filter(status__in=[SyncJob.Status.QUEUED, SyncJob.Status.RUNNING]).exists()
        if active_jobs:
            return Response({"error": "A sync job is already running for this store."}, status=status.HTTP_409_CONFLICT)
            
        start_history_import.delay(store.id)
        return Response({"status": "queued"})

    @action(detail=True, methods=["get"], url_path="sync-status")
    def sync_status(self, request, pk=None):
        store = self.get_object()
        latest_job = store.sync_jobs.order_by("-created_at").first()
        if not latest_job:
            return Response({"status": "no_job_found"})
            
        return Response(SyncJobSerializer(latest_job).data)

