"""
Django settings for tsl_manager_project.
This file contains configuration for the Django framework and is designed
to be environment-agnostic. Environment variables are used for all sensitive data.
"""

import os
from pathlib import Path

# === BASE DIRECTORY ===
# Project root directory (used for building paths)
BASE_DIR = Path(__file__).resolve().parent.parent

# === SECURITY SETTINGS ===
# Security key for cryptographic signing - keep this secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# Debug mode should be disabled in production environments
DEBUG = os.getenv("DEBUG") == "True"

# Hosts allowed to connect to the server
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# === APPLICATIONS ===
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "django_bootstrap5",
    "django_filters",
    # Local apps
    "tsl_manager_app",
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# === URL CONFIGURATION ===
ROOT_URLCONF = "tsl_manager_project.urls"

# === TEMPLATES ===
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Global templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# === WSGI CONFIGURATION ===
WSGI_APPLICATION = "tsl_manager_project.wsgi.application"

# === DATABASE CONFIGURATION ===
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        # "HOST": "postgres_database",
        # "PORT": "5432",
    }
}
# === PASSWORD VALIDATION ===
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# === INTERNATIONALIZATION ===
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

# === STATIC & MEDIA FILES ===
STATIC_URL = "/static/"
# STATIC_ROOT = BASE_DIR / "static"
# (dla developmentu, jeśli trzymasz np. app.css w katalogu 'static')
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# === DEFAULT FIELD CONFIGURATION ===
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# === AUTHENTICATION REDIRECTS ===
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "new_services"
LOGOUT_REDIRECT_URL = "greeting_view"

# === CUSTOM PROJECT PATHS ===
# DATA_DIRECTORY = BASE_DIR / "tsl_downloads"
# DATA_DIRECTORY = BASE_DIR / "send_to_db" / "data" / "data1"
# DATA_DIRECTORY = r"/code/tsl_downloads"

# === DJANGO BOOTSTRAP 5 CONFIGURATION ===
BOOTSTRAP5 = {
    "css_url": None,
    "javascript_url": None,
    "theme_url": None,
    "javascript_in_head": False,
    "wrapper_class": "mb-3",
    "inline_wrapper_class": "",
    "horizontal_label_class": "col-sm-2",
    "horizontal_field_class": "col-sm-8",
    "horizontal_field_offset_class": "offset-sm-2",
    "set_placeholder": True,
    "required_css_class": "",
    "error_css_class": "",
    "success_css_class": "",
    "server_side_validation": False,
    "formset_renderers": {
        "default": "django_bootstrap5.renderers.FormsetRenderer",
    },
    "form_renderers": {
        "default": "django_bootstrap5.renderers.FormRenderer",
    },
    "field_renderers": {
        "default": "django_bootstrap5.renderers.FieldRenderer",
    },
}
