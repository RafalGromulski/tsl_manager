#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
Modified to support dynamic Django settings module selection.
If DJANGO_ENV is 'production', it uses 'settings.production';
otherwise, it uses 'settings.development'.
"""
import os
import sys

if os.environ.get("DJANGO_ENV", "development") != "production":
    from dotenv import load_dotenv
    load_dotenv()


def main():
    """Run administrative tasks."""
    if os.environ.get("DJANGO_ENV", "development") != "production":
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tsl_manager_project.settings.development")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tsl_manager_project.settings.production")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
