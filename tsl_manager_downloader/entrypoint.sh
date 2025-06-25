#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "✅ Setting permissions for /app/tsl_downloads and /app/logs..."
mkdir -p /app/tsl_downloads /app/logs

# Set ownership to the current user (non-root)
chown -R celeryuser:celeryuser /app/tsl_downloads /app/logs

# Optional: Warn if directories are still not writable
if [ ! -w /app/tsl_downloads ] || [ ! -w /app/logs ]; then
  echo "❌ One or more target directories are not writable!"
  ls -ld /app/tsl_downloads /app/logs
  exit 1
fi

echo "🚀 Starting Celery worker..."
exec celery -A celery_app worker \
    --loglevel=info \
    -E \
    --hostname="downloader@$(hostname)" \
    -Q tsl
