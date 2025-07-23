"""
Production settings for tsl_manager_project.
Use this configuration only in production environments.
"""

from .base import *

# Debug mode should be disabled in production environments
DEBUG = False

# Hosts allowed to connect to the server
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# === DATABASE CONFIGURATION ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": "postgres_database",
        "PORT": "5432",
    }
}

# === STATIC FILES ===
STATIC_ROOT = BASE_DIR / "static"

# === CUSTOM PROJECT PATHS ===
DATA_DIRECTORY = Path("/code/tsl_downloads")
