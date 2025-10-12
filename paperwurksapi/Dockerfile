# =============================================================================
# Stage 1: Base
# =============================================================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pip-tools

# =============================================================================
# Stage 2: Dependencies (Core packages from base.in)
# =============================================================================
FROM base AS dependencies

COPY requirements/ requirements/

WORKDIR /app/requirements

RUN pip-compile base.in -o base.txt
RUN pip install --no-cache-dir -r base.txt

WORKDIR /app

# =============================================================================
# Stage 3: Development
# =============================================================================
FROM dependencies AS development

WORKDIR /app/requirements
RUN pip-compile dev.in -o dev.txt
RUN pip install --no-cache-dir -r dev.txt

WORKDIR /app

COPY . .

RUN mkdir -p /app/staticfiles

EXPOSE 8000

COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=apps.config.settings.development \
    ENVIRONMENT=development

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =============================================================================
# Stage 4: Test
# =============================================================================
FROM development AS test

ENV DJANGO_SETTINGS_MODULE=apps.config.settings.test \
    ENVIRONMENT=test

CMD ["pytest", "--cov=apps", "--cov-report=xml", "--cov-report=term-missing"]

# =============================================================================
# Stage 5: Production Builder (Collect Static)
# =============================================================================
FROM dependencies AS builder

WORKDIR /app/requirements
RUN pip-compile prod.in -o prod.txt
RUN pip install --no-cache-dir -r prod.txt

WORKDIR /app

COPY . .

RUN mkdir -p /app/staticfiles /app/mediafiles

ENV DJANGO_SETTINGS_MODULE=apps.config.settings.production \
    ENVIRONMENT=production \
    SECRET_KEY=build-time-secret \
    DEBUG=False

RUN python manage.py collectstatic --noinput

# =============================================================================
# Stage 6: Production
# =============================================================================
FROM base AS production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

RUN useradd -m -u 1000 appuser

WORKDIR /app
RUN chown -R appuser:appuser /app

USER appuser
COPY --chown=appuser:appuser . .
COPY --from=builder --chown=appuser:appuser /app/staticfiles /app/staticfiles

EXPOSE 8000

COPY --chown=appuser:appuser scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=apps.config.settings.production \
    ENVIRONMENT=production

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "apps.config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--log-file", "-", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info"]

# =============================================================================
# Stage 7: Worker
# =============================================================================
FROM production AS worker

USER appuser

HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD celery -A apps.config inspect ping -d celery@$HOSTNAME || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "apps.config", "worker", \
     "--loglevel=info", \
     "--concurrency=2", \
     "--max-tasks-per-child=1000"]