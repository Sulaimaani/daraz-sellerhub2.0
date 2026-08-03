from django.urls import reverse
from rest_framework.test import APITestCase


class AuthThrottlingTests(APITestCase):
    def test_login_throttling(self):
        url = reverse("login")
        # DRF ScopedRateThrottle for 'auth' is set to 5/hour in base.py
        # We'll hit the login endpoint 6 times. The 6th should be 429 Too Many Requests.

        for i in range(5):
            response = self.client.post(
                url, {"email": "test@example.com", "password": "wrongpassword"}
            )
            self.assertEqual(response.status_code, 401)

        # 6th request should be throttled
        response = self.client.post(
            url, {"email": "test@example.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 429)
