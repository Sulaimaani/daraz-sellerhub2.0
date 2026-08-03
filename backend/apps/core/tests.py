from django.test import TestCase
from django.conf import settings
from .crypto import decrypt_value, encrypt_value
from .daraz.signature import sign_request
from rest_framework.test import APIClient
from apps.accounts.models import User
from .tenancy import TenantQuerySet, TenantManager, IsStoreOwner
from .models import TimeStampedModel
from django.db import models
from rest_framework import viewsets, mixins, serializers
from rest_framework.response import Response

class ThrowawayTenantModel(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    objects = TenantManager.from_queryset(TenantQuerySet)()

class ThrowawaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ThrowawayTenantModel
        fields = ('id', 'name')

class ThrowawayViewSet(viewsets.ModelViewSet):
    queryset = ThrowawayTenantModel.objects.all()
    serializer_class = ThrowawaySerializer
    permission_classes = [IsStoreOwner]

class CryptoTests(TestCase):
    def test_encryption_decryption(self):
        original = "super_secret_token_123"
        encrypted = encrypt_value(original)
        self.assertNotEqual(original, encrypted)
        decrypted = decrypt_value(encrypted)
        self.assertEqual(original, decrypted)

    def test_empty_string(self):
        self.assertEqual(encrypt_value(""), "")
        self.assertEqual(decrypt_value(""), "")

class SignatureTests(TestCase):
    def test_sign_request(self):
        secret = "testsecret"
        api_path = "/order/get"
        parameters = {
            "app_key": "testkey",
            "timestamp": "1620000000000",
            "sign_method": "sha256",
            "access_token": "testtoken",
            "order_id": "12345"
        }
        signature = sign_request(secret, api_path, parameters)
        
        # Calculate manually to verify
        import hashlib
        import hmac
        expected_str = "/order/getaccess_tokentesttokenapp_keytestkeyorder_id12345sign_methodsha256timestamp1620000000000"
        expected_sig = hmac.new(secret.encode('utf-8'), expected_str.encode('utf-8'), hashlib.sha256).hexdigest().upper()
        
        self.assertEqual(signature, expected_sig)

class TenancyTests(TestCase):
    def setUp(self):
        self.client_a = APIClient()
        self.client_b = APIClient()
        
        self.user_a = User.objects.create_user(email="a@example.com", password="password")
        self.user_b = User.objects.create_user(email="b@example.com", password="password")
        
        self.client_a.force_authenticate(user=self.user_a)
        self.client_b.force_authenticate(user=self.user_b)
        
        from apps.accounts.models import UserProfile
        self.item_a = UserProfile.objects.create(user=self.user_a, business_name="A")
        self.item_b = UserProfile.objects.create(user=self.user_b, business_name="B")

    def test_tenant_queryset_filters_by_user(self):
        from apps.accounts.models import UserProfile
        # Since UserProfile doesn't have a store__owner path, let's just mock a model that does.
        # But we can't create one in SQLite easily inside atomic block.
        # So we will mock the filter method instead to test TenantQuerySet
        
        class MockQuerySet(TenantQuerySet):
            def filter(self, store__owner):
                return f"Filtered for {store__owner}"
                
        qs = MockQuerySet()
        self.assertEqual(qs.for_user(self.user_a), f"Filtered for {self.user_a}")

    def test_is_store_owner_permission(self):
        perm = IsStoreOwner()
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
                
        class MockStore:
            def __init__(self, owner):
                self.owner = owner
                
        class MockObject:
            def __init__(self, store):
                self.store = store
                
        req_a = MockRequest(self.user_a)
        req_b = MockRequest(self.user_b)
        
        item = MockObject(MockStore(self.user_a))
        
        self.assertTrue(perm.has_object_permission(req_a, None, item))
        self.assertFalse(perm.has_object_permission(req_b, None, item))
