"""
Django settings for Paperwurks Backend
Supports multiple environments: development, staging, production
"""

import os
from pathlib import Path
from decouple import config, Csv
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# Environment Detection
# =============================================================================
ENVIRONMENT = config("ENVIRONMENT", default="development")
DEBUG = config("DEBUG", default=False, cast=bool)

# =============================================================================
# Security Settings
# =============================================================================
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-in-production")

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://localhost:5173",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

# Security settings for production
if ENVIRONMENT == "production":
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# =============================================================================
# Application Definition
# =============================================================================

INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "corsheaders",
    "django_filters",
    "storages",
    # Local apps
    "apps.users",
    "apps.properties",
    "apps.documents",
    "apps.packs",
    "apps.searches",
    "apps.audit",
    "core",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Must be before CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RequestLoggingMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# =============================================================================
# Database Configuration
# =============================================================================

# AWS Secrets Manager integration for staging/production
if ENVIRONMENT in ["staging", "production"]:
    try:
        import boto3
        import json

        # Fetch database credentials from AWS Secrets Manager
        secret_name = f"paperwurks/{ENVIRONMENT}/database/master-credentials"
        region_name = config("AWS_REGION", default="eu-west-2")

        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response["SecretString"])

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": secret["dbname"],
                "USER": secret["username"],
                "PASSWORD": secret["password"],
                "HOST": secret["host"],
                "PORT": secret["port"],
                "CONN_MAX_AGE": 600,
                "OPTIONS": {
                    "connect_timeout": 10,
                    "options": "-c statement_timeout=30000",  # 30 seconds
                },
            }
        }
    except Exception as e:
        # Fallback to environment variables if Secrets Manager fails
        print(f"Warning: Could not fetch secrets from AWS: {e}")
        print("Falling back to environment variables")
        DATABASES = {
            "default": dj_database_url.config(
                default=f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}",
                conn_max_age=600,
            )
        }
else:
    # Development/Test - Use environment variables
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME", default="paperwurks_dev"),
            "USER": config("DB_USER", default="postgres"),
            "PASSWORD": config("DB_PASSWORD", default="postgres"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432", cast=int),
            "CONN_MAX_AGE": 0 if ENVIRONMENT == "test" else 600,
            "ATOMIC_REQUESTS": True,
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }

# Test database configuration
if ENVIRONMENT == "test":
    DATABASES["default"]["TEST"] = {
        "NAME": "test_paperwurks",
    }

# =============================================================================
# Authentication & User Model
# =============================================================================

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# JWT Configuration
JWT_SECRET_KEY = config("JWT_SECRET_KEY", default=SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_LIFETIME = config("JWT_ACCESS_TOKEN_LIFETIME", default=3600, cast=int)  # 1 hour
JWT_REFRESH_TOKEN_LIFETIME = config("JWT_REFRESH_TOKEN_LIFETIME", default=604800, cast=int)  # 7 days

# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# =============================================================================
# Static Files (CSS, JavaScript, Images)
# =============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

# =============================================================================
# Media Files (User uploads)
# =============================================================================

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# =============================================================================
# AWS S3 Storage Configuration
# =============================================================================

AWS_REGION = config("AWS_REGION", default="eu-west-2")
AWS_STORAGE_BUCKET_NAME = config(
    "AWS_STORAGE_BUCKET_NAME", 
    default=f"paperwurks-{ENVIRONMENT}-documents"
)

# LocalStack for local development
AWS_ENDPOINT_URL = config("AWS_ENDPOINT_URL", default=None)
if AWS_ENDPOINT_URL:
    AWS_S3_ENDPOINT_URL = AWS_ENDPOINT_URL
    AWS_S3_USE_SSL = False
    AWS_S3_VERIFY = False

# AWS credentials (use IAM roles in production)
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default=None)
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default=None)

# S3 storage settings
AWS_S3_CUSTOM_DOMAIN = None
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",  # 1 day
}
AWS_DEFAULT_ACL = "private"
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 3600  # 1 hour

# Use S3 for media files in staging/production
if ENVIRONMENT in ["staging", "production"]:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
else:
    # Use local storage for development
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# =============================================================================
# Celery Configuration
# =============================================================================

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# For tests, run tasks synchronously
if ENVIRONMENT == "test":
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# =============================================================================
# Cache Configuration
# =============================================================================

if ENVIRONMENT in ["staging", "production"]:
    # Use Redis for caching in staging/production
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": f"paperwurks_{ENVIRONMENT}",
            "TIMEOUT": 300,  # 5 minutes default
        }
    }
else:
    # Use local memory cache for development
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "paperwurks-cache",
        }
    }

# =============================================================================
# Email Configuration
# =============================================================================

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

if ENVIRONMENT in ["staging", "production"]:
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.sendgrid.net")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@paperwurks.com")
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

# =============================================================================
# Logging Configuration
# =============================================================================

LOG_LEVEL = config("LOG_LEVEL", default="INFO" if ENVIRONMENT == "production" else "DEBUG")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {name} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "paperwurks.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO" if DEBUG else "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"] if ENVIRONMENT == "production" else ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
    },
}

# =============================================================================
# Third-party Integrations
# =============================================================================

# Sentry (Error Tracking)
SENTRY_DSN = config("SENTRY_DSN", default=None)
if SENTRY_DSN and ENVIRONMENT in ["staging", "production"]:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1 if ENVIRONMENT == "production" else 1.0,
        send_default_pii=False,
    )

# New Relic (APM)
NEW_RELIC_LICENSE_KEY = config("NEW_RELIC_LICENSE_KEY", default=None)
NEW_RELIC_APP_NAME = config(
    "NEW_RELIC_APP_NAME",
    default=f"paperwurks-backend-{ENVIRONMENT}",
)

# =============================================================================
# Django Ninja API Configuration
# =============================================================================

NINJA_PAGINATION_CLASS = "ninja.pagination.PageNumberPagination"
NINJA_PAGINATION_PER_PAGE = 20

# =============================================================================
# Default Auto Field
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# Feature Flags
# =============================================================================

ENABLE_AI_ANALYSIS = config("ENABLE_AI_ANALYSIS", default=True, cast=bool)
ENABLE_DOCUMENT_PROCESSING = config("ENABLE_DOCUMENT_PROCESSING", default=True, cast=bool)
ENABLE_SEARCH_INTEGRATION = config("ENABLE_SEARCH_INTEGRATION", default=False, cast=bool)

# =============================================================================
# Development-only Settings
# =============================================================================

if DEBUG and ENVIRONMENT == "development":
    # Django Debug Toolbar
    try:
        import debug_toolbar
        INSTALLED_APPS += ["debug_toolbar"]
        MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
        INTERNAL_IPS = ["127.0.0.1", "localhost"]
    except ImportError:
        pass

    # Django Extensions
    try:
        import django_extensions
        INSTALLED_APPS += ["django_extensions"]
    except ImportError:
        pass

# =============================================================================
# Test Settings
# =============================================================================

if ENVIRONMENT == "test":
    # Speed up password hashing in tests
    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ]
    
    # Disable migrations for faster tests
    class DisableMigrations:
        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return None

    # MIGRATION_MODULES = DisableMigrations()  # Uncomment for faster tests

# Create logs directory if it doesn't exist
(BASE_DIR / "logs").mkdir(exist_ok=True)