"""
Development settings for tsl_manager_project.
Use this configuration only during local development.
"""

from .base import *

# Debug mode should be disabled in production environments
DEBUG = True

# Hosts allowed to connect to the server
ALLOWED_HOSTS = ["*"]

# === DATABASE CONFIGURATION ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

# === STATIC FILES ===
STATICFILES_DIRS = [BASE_DIR / "static"]

# === CUSTOM PROJECT PATHS ===
DATA_DIRECTORY = BASE_DIR / "send_to_db" / "data" / "data1"
