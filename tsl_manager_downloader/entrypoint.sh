#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "📂 Ensuring required directories exist..."
mkdir -p /app/tsl_downloads /app/logs

echo "🚀 Starting Celery worker..."
exec celery -A celery_app worker \
    --loglevel=info \
    -E \
    --hostname="downloader@$(hostname)" \
    -Q tsl
