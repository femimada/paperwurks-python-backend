"""
Build-time settings - used only during Docker image creation
"""
from .common import *

DEBUG = False
SECRET_KEY = "build-time-secret-key-not-for-runtime"

# Minimal database for collectstatic
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# No cache needed for build
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}


CELERY_TASK_ALWAYS_EAGER = True