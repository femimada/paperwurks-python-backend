# =============================================================================
# Stage 1: Base - Python 3.12 with system dependencies
# =============================================================================
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies required for PostgreSQL and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pip-tools
# =============================================================================
# Stage 2: Dependencies - Install Python packages
# =============================================================================
FROM base AS dependencies

COPY requirements.in .
RUN pip-compile requirements.in -o requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 3: Development - Includes dev tools and hot-reload
# =============================================================================
FROM dependencies AS development

# Install development dependencies
COPY requirements-dev.in .
RUN pip-compile requirements-dev.in -o requirements-dev.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles

# Expose Django development server port
EXPOSE 8000

# Copy entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# =============================================================================
# Stage 4: Test - Optimized for CI/CD testing
# =============================================================================
FROM development AS test

# Set testing environment
ENV DJANGO_SETTINGS_MODULE=config.settings \
    ENVIRONMENT=test

# Run tests by default
CMD ["pytest", "--cov=apps", "--cov-report=xml", "--cov-report=term-missing"]

# =============================================================================
# Stage 5: Production Builder - Collect static files
# =============================================================================
FROM dependencies AS builder

COPY . .
RUN mkdir -p /app/staticfiles /app/mediafiles

# Collect static files (Django admin, etc.)
ENV DJANGO_SETTINGS_MODULE=config.settings \
    ENVIRONMENT=production \
    SECRET_KEY=build-time-secret \
    DEBUG=False

RUN python manage.py collectstatic --noinput

# =============================================================================
# Stage 6: Production - Minimal runtime image
# =============================================================================
FROM base AS production

# Install only runtime dependencies (no gcc, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Copy collected static files from builder
COPY --from=builder /app/staticfiles /app/staticfiles

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose Gunicorn port
EXPOSE 8000

# Copy entrypoint script
COPY --chown=appuser:appuser scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
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
# Stage 7: Worker - Celery worker for async tasks
# =============================================================================
FROM dependencies as worker

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Copy entrypoint script
COPY --chown=appuser:appuser scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check for Celery worker
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD celery -A config inspect ping -d celery@$HOSTNAME || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["celery", "-A", "config", "worker", \
     "--loglevel=info", \
     "--concurrency=2", \
     "--max-tasks-per-child=1000"]