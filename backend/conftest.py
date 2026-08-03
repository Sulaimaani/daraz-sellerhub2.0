import factory
import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserProfile


@pytest.fixture
def api_client():
    return APIClient()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    is_active = True
    email_verified = True


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)
    business_name = factory.Faker("company")
    phone = factory.Faker("phone_number")
    timezone = "Asia/Karachi"


@pytest.fixture
def user():
    user = UserFactory()
    UserProfileFactory(user=user)
    return user


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
