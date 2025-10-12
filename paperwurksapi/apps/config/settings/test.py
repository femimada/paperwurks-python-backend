# apps/config/settings/test.py

from .common import *

# =============================================================================
# TEST OVERRIDES
# =============================================================================

DEBUG = False
# Speed up password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use an in-memory database for speed (default if DATABASE_URL isn't specified)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Optional: Disable migrations for faster tests (must be placed outside the class)
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations() # Uncomment this line for extreme speedup

# Force environment variable reading to use fast defaults if not set
SECRET_KEY = "test-secret"
ALLOWED_HOSTS = ["testserver"]