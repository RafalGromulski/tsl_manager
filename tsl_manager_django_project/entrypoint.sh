#!/usr/bin/env sh

echo "Environment loaded via Docker Compose"

echo "📁 Ensuring /code/tsl_downloads exists..."
mkdir -p /code/tsl_downloads

echo "Starting Django application setup..."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="${DJANGO_SUPERUSER_USERNAME}").exists():
    User.objects.create_superuser(
    "${DJANGO_SUPERUSER_USERNAME}",
    "${DJANGO_SUPERUSER_EMAIL}",
    "${DJANGO_SUPERUSER_PASSWORD}"
    )
EOF

echo "🚀 Django setup complete. Starting production server..."
exec gunicorn tsl_manager_project.wsgi:application --bind 0.0.0.0:8000
