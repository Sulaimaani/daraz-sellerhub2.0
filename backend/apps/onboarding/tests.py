import pytest
from django.urls import reverse
from apps.accounts.models import User
from apps.stores.models import Store

pytestmark = pytest.mark.django_db

# UNVERIFIED TESTS: Written for Postgres but unexecuted locally.

@pytest.fixture
def user_a():
    return User.objects.create_user(email="user_a@test.com", password="password")

@pytest.fixture
def auth_client(client, user_a):
    client.force_login(user_a)
    return client

class TestOnboardingState:
    
    def test_get_initial_state(self, auth_client):
        res = auth_client.get(reverse("onboarding-state"))
        assert res.status_code == 200
        assert res.data["current_step"] == 1

    def test_advance_to_step_2(self, auth_client):
        res = auth_client.post(reverse("onboarding-step"), {"step": 2})
        assert res.status_code == 200
        assert res.data["current_step"] == 2

    def test_advance_past_step_2_without_store_fails(self, auth_client):
        res = auth_client.post(reverse("onboarding-step"), {"step": 3})
        assert res.status_code == 403
        assert "must connect a store" in res.data["error"]

    def test_advance_past_step_2_with_store_succeeds(self, auth_client, user_a):
        Store.objects.create(owner=user_a, daraz_seller_id="123", status=Store.Status.CONNECTED)
        res = auth_client.post(reverse("onboarding-step"), {"step": 3})
        assert res.status_code == 200
        assert res.data["current_step"] == 3
