from .common import *

# =============================================================================
# PRODUCTION OVERRIDES
# =============================================================================

DEBUG = False
SECRET_KEY = config("SECRET_KEY") 
DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": f"paperwurks_{ENVIRONMENT}",
        "TIMEOUT": 300,
    }
}

# =============================================================================
# Security Enforcement
# =============================================================================

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)

SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv()) 
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")

# =============================================================================
# AWS/S3 Storage Configuration (FULLY CONSOLIDATED)
# =============================================================================

AWS_REGION = config("AWS_REGION", default="eu-west-2")
AWS_STORAGE_BUCKET_NAME = config(
    "AWS_STORAGE_BUCKET_NAME", 
    default=f"paperwurks-{ENVIRONMENT}-documents"
)

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default=None)
AWS_DEFAULT_ACL = 'public-read' 
AWS_AUTO_CREATE_BUCKET = True 

# Set default file storage to S3
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Set MEDIA_URL to S3 location for file serving
MEDIA_URL = f'https://s3.{AWS_REGION}.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/'

# =============================================================================
# Email Configuration
# =============================================================================

EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@paperwurks.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL