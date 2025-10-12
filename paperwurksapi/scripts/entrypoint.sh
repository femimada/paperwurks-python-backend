#!/bin/bash
set -e

# =============================================================================
# Docker Entrypoint Script for Paperwurks Backend
# =============================================================================

echo "Starting Paperwurks Backend..."

# Wait for database to be ready
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
    
    max_retries=30
    retry_count=0
    
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1 || [ $retry_count -eq $max_retries ]; do
        retry_count=$((retry_count + 1))
        echo "   Attempt $retry_count/$max_retries: Database not ready yet..."
        sleep 2
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo " Database connection timeout after $max_retries attempts"
        exit 1
    fi
    
    echo "Database is ready!"
fi

# Wait for Redis to be ready
if [ -n "$REDIS_URL" ]; then
    echo "Waiting for Redis..."
    
    max_retries=30
    retry_count=0
    
    # Extract host and port from REDIS_URL
    REDIS_HOST=$(echo $REDIS_URL | sed -E 's|redis://(:.*@)?([^:]+):.*|\2|')
    REDIS_PORT=$(echo $REDIS_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
    
    until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1 || [ $retry_count -eq $max_retries ]; do
        retry_count=$((retry_count + 1))
        echo "   Attempt $retry_count/$max_retries: Redis not ready yet..."
        sleep 2
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "⚠️  Redis connection timeout, continuing anyway..."
    else
        echo "Redis is ready!"
    fi
fi

# Run database migrations in production/staging environments
if [ "$ENVIRONMENT" = "production" ] || [ "$ENVIRONMENT" = "staging" ]; then
    echo " Running database migrations..."
    python manage.py migrate --noinput
    echo "Migrations complete!"
    
    # Collect static files (already done in build, but ensures it's up to date)
    echo "Collecting static files..."
    python manage.py collectstatic --noinput --clear
    echo "Static files collected!"
fi

# Create superuser in development if it doesn't exist
if [ "$ENVIRONMENT" = "development" ]; then
    echo " Running database migrations..."
    python manage.py migrate --noinput
    
    echo "Creating superuser if needed..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@paperwurks.local').exists():
    User.objects.create_superuser(
        email='admin@paperwurks.local',
        password='admin',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created: admin@paperwurks.local / admin')
else:
    print('Superuser already exists')
END
fi

# Print environment info
echo ""
echo "Environment Information:"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   DEBUG: ${DEBUG:-False}"
echo "   DATABASE: $DB_NAME@$DB_HOST:$DB_PORT"
echo "   ALLOWED_HOSTS: ${ALLOWED_HOSTS:-not set}"
echo ""

# Execute the main command
echo "Executing command: $@"
exec "$@"