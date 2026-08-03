from .base import *

DEBUG = False

# HTTPS only
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Email backend for production (e.g., Anymail with Resend)
EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
ANYMAIL = {
    "RESEND_API_KEY": env("RESEND_API_KEY", default=""),
}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@darazsaas.com")
