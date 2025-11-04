"""
WSGI config for project.

This file has been modified to support dynamic Django settings module selection
based on the DJANGO_ENV environment variable. If DJANGO_ENV is set to 'production',
it loads 'settings.production'; otherwise, it defaults to 'settings.development'.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

from config.env import configure_django_settings
from django.core.wsgi import get_wsgi_application

configure_django_settings()

application = get_wsgi_application()
