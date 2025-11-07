"""
ASGI config for project.

This file has been modified to support dynamic Django settings module selection
based on the DJANGO_ENV environment variable. If DJANGO_ENV is set to 'production',
it loads 'settings.production'; otherwise, it defaults to 'settings.development'.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

from django.core.asgi import get_asgi_application

from .env import configure_django_settings

configure_django_settings()

application = get_asgi_application()
