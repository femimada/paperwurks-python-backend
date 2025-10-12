from .common import *

# =============================================================================
# DEVELOPMENT OVERRIDES
# =============================================================================

DEBUG = True

DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///" + str(BASE_DIR / "db.sqlite3"), conn_max_age=600
    )
}


EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' 

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"