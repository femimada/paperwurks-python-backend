"""
Celery configuration for Paperwurks Backend
"""

import os
from celery import Celery
from decouple import config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Get environment
ENVIRONMENT = config("ENVIRONMENT", default="development")

app = Celery(
    "paperwurks",
    broker=config("CELERY_BROKER_URL", default="redis://localhost:6379/0"),
    backend=config("CELERY_RESULT_BACKEND", default="redis://localhost:6379/0"),
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery based on environment
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/London",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Task routes - send specific tasks to specific queues
app.conf.task_routes = {
    "tasks.document_processing.*": {"queue": "document_processing"},
    "tasks.ai_analysis.*": {"queue": "ai_analysis"},
    "tasks.search_ordering.*": {"queue": "search_ordering"},
    "tasks.notifications.*": {"queue": "notifications"},
}

# Celery Beat Schedule (Periodic Tasks)
from celery.schedules import crontab

app.conf.beat_schedule = {
    # Example: Clean up expired documents every day at 2 AM
    "cleanup-expired-documents": {
        "task": "tasks.document_processing.cleanup_expired_documents",
        "schedule": crontab(hour=2, minute=0),
    },
    # Example: Send daily summary emails
    "send-daily-summaries": {
        "task": "tasks.notifications.send_daily_summaries",
        "schedule": crontab(hour=8, minute=0),
    },
    # Example: Check for stale property packs
    "check-stale-packs": {
        "task": "tasks.document_processing.check_stale_packs",
        "schedule": crontab(hour=9, minute=0, day_of_week="monday"),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")
    return f"Debug task executed in {ENVIRONMENT} environment"