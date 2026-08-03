from .base import *

DEBUG = False

# Strict Environment Variable Parsing
# This configuration intentionally fails loudly if required variables are missing

DATABASE_URL = env.db("DATABASE_URL")
DATABASES = {"default": DATABASE_URL}

REDIS_URL = env.str("REDIS_URL")

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Daraz OAuth
DARAZ_APP_KEY = env.str("DARAZ_APP_KEY")
DARAZ_APP_SECRET = env.str("DARAZ_APP_SECRET")
DARAZ_REDIRECT_URI = env.str("DARAZ_REDIRECT_URI")
DARAZ_MOCK = env.bool("DARAZ_MOCK", default=False)

# DigitalOcean Spaces (S3)
AWS_ACCESS_KEY_ID = env.str("SPACES_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("SPACES_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("SPACES_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = env.str("SPACES_ENDPOINT_URL")
AWS_S3_REGION_NAME = env.str("SPACES_REGION_NAME")
AWS_S3_CUSTOM_DOMAIN = env.str("SPACES_CUSTOM_DOMAIN", default=None)

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}

# Domains and CORS
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# JWT Security overrides for production
SIMPLE_JWT["AUTH_COOKIE_SECURE"] = True
SIMPLE_JWT["AUTH_COOKIE_SAMESITE"] = "Lax"
SIMPLE_JWT["AUTH_COOKIE_DOMAIN"] = env.str("AUTH_COOKIE_DOMAIN")
