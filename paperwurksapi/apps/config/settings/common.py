from pathlib import Path
from decouple import config, Csv
import dj_database_url
from django.utils.log import DEFAULT_LOGGING

# BASE_DIR is four levels up (common.py -> settings -> config -> apps -> root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# =============================================================================
# Core Project Settings
# =============================================================================
ENVIRONMENT = config("ENVIRONMENT", default="development")
DEBUG = config("DEBUG", default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-in-production")
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# Apps
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
    "ninja",
    # Local apps
    #"apps.users",
    "apps.config",
]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "apps.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "apps.config.wsgi.application"
ASGI_APPLICATION = "apps.config.asgi.application"


# =============================================================================
# Database
# =============================================================================

DATABASES = {
    "default": dj_database_url.config(conn_max_age=600)
}

# =============================================================================
# Auth, Password Validation, and User Model
# =============================================================================

#AUTH_USER_MODEL = "apps.users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =============================================================================
# Internationalization
# =============================================================================

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True


# =============================================================================
# Static files (CSS, JavaScript, Images) and Media files
# =============================================================================

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "mediafiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =============================================================================
# CORS & Security
# =============================================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://localhost:5173",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True


# =============================================================================
# Celery, Cache, and Feature Flags ✨
# =============================================================================

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = 30 * 60

ENABLE_DOCUMENT_PROCESSING = config("ENABLE_DOCUMENT_PROCESSING", default=True, cast=bool)
ENABLE_SEARCH_INTEGRATION = config("ENABLE_SEARCH_INTEGRATION", default=False, cast=bool)


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "paperwurks-cache",
    }
}

# =============================================================================
# Logging Configuration
# =============================================================================

# LOG_LEVEL = config("LOG_LEVEL", default="INFO")

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "[{levelname}] {asctime} {name} {message}",
#             "style": "{",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#         "simple": {
#             "format": "[{levelname}] {message}",
#             "style": "{",
#         },
#     },
#     "handlers": {
#         "console": {
#             "level": LOG_LEVEL,
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": LOG_LEVEL,
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#         "django.db.backends": {
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "celery": {
#             "handlers": ["console"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#         "apps": {
#             "handlers": ["console"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#     },
# }


(BASE_DIR / "logs").mkdir(exist_ok=True)