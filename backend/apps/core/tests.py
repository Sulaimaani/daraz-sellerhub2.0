from django.test import TestCase

from .crypto import decrypt_value, encrypt_value


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


from .daraz.signature import sign_request


class SignatureTests(TestCase):
    def test_sign_request(self):
        secret = "testsecret"
        api_path = "/order/get"
        parameters = {
            "app_key": "testkey",
            "timestamp": "1620000000000",
            "sign_method": "sha256",
            "access_token": "testtoken",
            "order_id": "12345",
        }
        # Sorted keys: access_token, app_key, order_id, sign_method, timestamp
        # Concatenated: /order/getaccess_tokentesttokenapp_keytestkeyorder_id12345sign_methodsha256timestamp1620000000000
        signature = sign_request(secret, api_path, parameters)

        # Calculate manually to verify
        import hashlib
        import hmac

        expected_str = "/order/getaccess_tokentesttokenapp_keytestkeyorder_id12345sign_methodsha256timestamp1620000000000"
        expected_sig = (
            hmac.new(
                secret.encode("utf-8"), expected_str.encode("utf-8"), hashlib.sha256
            )
            .hexdigest()
            .upper()
        )

        self.assertEqual(signature, expected_sig)
