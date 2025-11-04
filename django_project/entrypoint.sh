#!/usr/bin/env sh

echo "Environment loaded via Docker Compose"

echo "📁 Ensuring /code/tsl_downloads exists..."
mkdir -p /code/tsl_downloads

echo "Starting Django application setup..."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ -n "${DJANGO_SUPERUSER_PASSWORD_FILE:-}" ] && [ -f "$DJANGO_SUPERUSER_PASSWORD_FILE" ]; then
  echo "[entrypoint] Using superuser password from file: $DJANGO_SUPERUSER_PASSWORD_FILE"
elif [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "[entrypoint] Using superuser password from env var"
else
  echo "[entrypoint] No superuser password provided (DJANGO_SUPERUSER_PASSWORD_FILE or DJANGO_SUPERUSER_PASSWORD)." >&2
fi

python manage.py ensure_superuser || {
  echo "[entrypoint] ensure_superuser failed — check secret mount/permissions." >&2
  exit 1
}

if [ "${DJANGO_SETTINGS_MODULE:-}" = "config.settings.prod" ]; then
  echo "Running Django deploy checks..."
  python manage.py check --deploy || true
fi

echo "🚀 Django setup complete. Starting production server..."
#exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -