import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.db import connection
from apps.stores.models import Store, OAuthState, OAuthToken, SyncJob, SyncWindow
from apps.accounts.models import User
from apps.core.daraz.client import DarazClient, DarazRateLimitError

pytestmark = pytest.mark.django_db

# UNVERIFIED TESTS: These tests were written for Postgres but have not been executed locally 
# due to the lack of a local Postgres service. They will be verified post-deployment on DigitalOcean.

@pytest.fixture
def user_a():
    return User.objects.create_user(email="user_a@test.com", password="password")

@pytest.fixture
def user_b():
    return User.objects.create_user(email="user_b@test.com", password="password")

@pytest.fixture
def auth_client(client, user_a):
    client.force_login(user_a)
    return client

class TestOAuthStateAndCallback:
    
    @patch("apps.core.daraz.client.DarazClient.create_token")
    @patch("apps.core.daraz.client.DarazClient.get_seller")
    def test_valid_round_trip(self, mock_get_seller, mock_create_token, auth_client, user_a):
        mock_create_token.return_value = {"access_token": "acc123", "refresh_token": "ref123", "account_id": "seller_1"}
        mock_get_seller.return_value = {"data": {"seller_id": "seller_1", "name": "Test Store"}}

        res = auth_client.post(reverse("store-connect"))
        assert res.status_code == 200
        state_obj = OAuthState.objects.get(user=user_a)
        
        callback_res = auth_client.get(reverse("store-callback"), {"code": "test_code", "state": state_obj.state})
        assert callback_res.status_code == 302
        
        state_obj.refresh_from_db()
        assert state_obj.consumed_at is not None
        assert Store.objects.filter(owner=user_a).exists()

    def test_state_older_than_10_minutes_rejected(self, auth_client, user_a):
        state_obj = OAuthState.objects.create(user=user_a, state="expired_state")
        OAuthState.objects.filter(id=state_obj.id).update(created_at=timezone.now() - timedelta(minutes=11))
        
        callback_res = auth_client.get(reverse("store-callback"), {"code": "test_code", "state": "expired_state"})
        assert "error=state_expired" in callback_res.url

    def test_consumed_state_rejected_on_reuse(self, auth_client, user_a):
        state_obj = OAuthState.objects.create(user=user_a, state="consumed_state", consumed_at=timezone.now())
        callback_res = auth_client.get(reverse("store-callback"), {"code": "test_code", "state": "consumed_state"})
        assert "error=state_already_consumed" in callback_res.url

    def test_state_issued_to_user_a_presented_by_user_b(self, client, user_a, user_b):
        state_obj = OAuthState.objects.create(user=user_a, state="user_a_state")
        client.force_login(user_b)
        callback_res = client.get(reverse("store-callback"), {"code": "test_code", "state": "user_a_state"})
        assert "error=cross_user_state" in callback_res.url

    @patch("apps.core.daraz.client.DarazClient.create_token")
    @patch("apps.core.daraz.client.DarazClient.get_seller")
    def test_reconnect_not_duplicate(self, mock_get_seller, mock_create_token, auth_client, user_a):
        mock_create_token.return_value = {"access_token": "acc123", "refresh_token": "ref123"}
        mock_get_seller.return_value = {"data": {"seller_id": "seller_1", "name": "Test Store"}}

        Store.objects.create(owner=user_a, daraz_seller_id="seller_1", name="Old Name")
        state_obj = OAuthState.objects.create(user=user_a, state="state_1")
        
        auth_client.get(reverse("store-callback"), {"code": "test_code", "state": "state_1"})
        
        assert Store.objects.count() == 1
        assert Store.objects.get().name == "Test Store"

    @patch("apps.core.daraz.client.DarazClient.create_token")
    @patch("apps.core.daraz.client.DarazClient.get_seller")
    def test_409_on_another_users_seller(self, mock_get_seller, mock_create_token, client, user_a, user_b):
        mock_create_token.return_value = {"access_token": "acc123", "refresh_token": "ref123"}
        mock_get_seller.return_value = {"data": {"seller_id": "shared_seller"}}

        Store.objects.create(owner=user_a, daraz_seller_id="shared_seller")
        
        client.force_login(user_b)
        state_obj = OAuthState.objects.create(user=user_b, state="state_b")
        
        callback_res = client.get(reverse("store-callback"), {"code": "test_code", "state": "state_b"})
        assert "store_already_connected_by_other_user" in callback_res.url


class TestSecurityAndCrypto:

    def test_raw_sql_plaintext_check_on_tokens(self, user_a):
        store = Store.objects.create(owner=user_a, daraz_seller_id="123")
        token_obj = OAuthToken.objects.create(
            store=store, 
            access_token="secret_access", 
            refresh_token="secret_refresh",
            access_expires_at=timezone.now(),
            refresh_expires_at=timezone.now()
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT access_token FROM stores_oauthtoken WHERE id = %s", [token_obj.id])
            row = cursor.fetchone()
            db_value = row[0]
            
            assert "secret_access" not in db_value
            assert db_value.startswith("gAAAAA") # fernet format check

    def test_redaction_assertions(self, user_a):
        store = Store.objects.create(owner=user_a, daraz_seller_id="123")
        client = DarazClient(store=store)
        client._log_call("/test", {"access_token": "super_secret"}, "response", 200, 100)
        
        from apps.stores.models import ApiCallLog
        log = ApiCallLog.objects.first()
        assert log.request_params["access_token"] == "***"
        assert "super_secret" not in str(log.request_params)


class TestClientAndTasks:

    @patch("requests.post")
    def test_refresh_failure_needs_reconnect(self, mock_post, user_a):
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"code": "InvalidAccessToken"}

        store = Store.objects.create(owner=user_a, daraz_seller_id="123", status=Store.Status.CONNECTED)
        token = OAuthToken.objects.create(
            store=store, access_token="old", refresh_token="old_r",
            access_expires_at=timezone.now(), refresh_expires_at=timezone.now(),
            refresh_failures=2
        )
        
        from apps.stores.tasks import refresh_expiring_tokens
        refresh_expiring_tokens()
        
        token.refresh_from_db()
        assert token.refresh_failures == 3
        store.refresh_from_db()
        assert store.status == Store.Status.NEEDS_RECONNECT

    @patch("requests.get")
    def test_429_backoff(self, mock_get, user_a):
        mock_get.return_value.status_code = 429
        client = DarazClient()
        
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(DarazRateLimitError):
                client.call("/test")
                
            assert mock_get.call_count == 5
            assert mock_sleep.call_count == 4

    def test_syncjob_resumability(self, user_a):
        store = Store.objects.create(owner=user_a, daraz_seller_id="123")
        job = SyncJob.objects.create(store=store, kind=SyncJob.Kind.HISTORY, status=SyncJob.Status.RUNNING)
        w1 = SyncWindow.objects.create(sync_job=job, date_from=timezone.now(), date_to=timezone.now(), status=SyncWindow.Status.FAILED)
        w2 = SyncWindow.objects.create(sync_job=job, date_from=timezone.now(), date_to=timezone.now(), status=SyncWindow.Status.COMPLETED)
        
        from apps.stores.tasks import process_sync_windows
        
        # When process_sync_windows runs, it should only pick up PENDING or FAILED (w1)
        with patch("apps.core.daraz.client.DarazClient.call") as mock_call:
            mock_call.return_value = {"data": {"orders": []}}
            process_sync_windows(job.id)
            
            w1.refresh_from_db()
            assert w1.status == SyncWindow.Status.COMPLETED
            assert w1.attempts == 1


class TestCrossTenantIsolation:

    def test_cross_tenant_isolation(self, client, user_a, user_b):
        Store.objects.create(owner=user_a, daraz_seller_id="123", name="A")
        store_b = Store.objects.create(owner=user_b, daraz_seller_id="456", name="B")
        
        client.force_login(user_a)
        res = client.get(reverse("store-list"))
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "A"
        
        res_b = client.get(reverse("store-sync-status", args=[store_b.id]))
        assert res_b.status_code == 404
