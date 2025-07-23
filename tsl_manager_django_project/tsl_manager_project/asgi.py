"""
ASGI config for tsl_manager_project project.

This file has been modified to support dynamic Django settings module selection
based on the DJANGO_ENV environment variable. If DJANGO_ENV is set to 'production',
it loads 'settings.production'; otherwise, it defaults to 'settings.development'.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from django.core.asgi import get_asgi_application

if os.environ.get("DJANGO_ENV", "development") != "production":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tsl_manager_project.settings.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tsl_manager_project.settings.production")

application = get_asgi_application()
