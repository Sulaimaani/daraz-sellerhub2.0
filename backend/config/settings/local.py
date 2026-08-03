from .base import *

# In local, we are fine with DEBUG=True and unsecured cookies.
DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Local cookies shouldn't require HTTPS.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
