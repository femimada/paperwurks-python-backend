#!/bin/bash
set -e

echo "Starting Paperwurks Backend..."

SERVICE_TYPE="backend" 
if [ "$SERVICE_TYPE" = "backend" ]; then 
    echo "Running database migrations..."
    python manage.py migrate --noinput
    echo "Migrations complete!"
    
fi

echo "Executing command: $@"
exec "$@"