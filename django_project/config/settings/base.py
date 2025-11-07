"""
Base Django settings for the Mini e-commerce Shop API.

This module defines configuration shared across all environments
(dev / production). Environment-specific overrides live in:
`dev.py` and `prod.py`.

Notes:
- Environment variables are loaded via `django-environ`.
- Where applicable, helpers are Docker-secrets friendly (e.g., *_FILE vars).
"""

from pathlib import Path
from typing import Any

import environ

# from urllib.parse import quote_plus


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
# Project root directory (used for building paths)
# => parents[2] points to <project_root>
BASE_DIR = Path(__file__).resolve().parents[2]
# Equivalent
# BASE_DIR = Path(__file__).resolve().parent.parent.parent

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, True),
)

# # Load .env if present (prefer <project_root>/.env; fall back to django_project/.env)
env_file_candidates = [PROJECT_ROOT / ".env", BASE_DIR / ".env"]
for _env_path in env_file_candidates:
    if _env_path.exists():
        environ.Env.read_env(_env_path)
        break


# ---------------------------------------------------------------------
# Secrets helpers / URL builders (Docker secrets friendly)
# ---------------------------------------------------------------------
def read_secret(path: str | None, default: str = "") -> str:
    """
    Read a secret from a file (e.g., `/run/secrets/...`); fall back to `default`.

    Args:
        path: Path to the secret file or None.
        default: Value to return when `path` is missing or unreadable.

    Returns:
        The stripped file contents on success, otherwise `default`.
    """
    if not path:
        return default
    try:
        return Path(path).read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return default


def build_postgres_dict_from_parts() -> dict[str, Any]:
    """
    Build `DATABASES['default']` using discrete DB_* envs + optional `DB_PASSWORD_FILE`.

    Honors:
        - DB_NAME, DB_USER, DB_HOST, DB_PORT
        - DB_CONN_MAX_AGE, DB_CONNECT_TIMEOUT
        - DB_SSL_REQUIRED, DB_SSLMODE
        - DB_PASSWORD_FILE (preferred) or POSTGRES_PASSWORD

    Returns:
        A Django DATABASES configuration dictionary for PostgreSQL.
    """
    name = env("DB_NAME", default="app")
    user = env("DB_USER", default="app")
    host = env("DB_HOST", default="postgres")
    # host = env("DB_HOST", default="db")
    port = env("DB_PORT", default="5432")
    pwd = read_secret(env("DB_PASSWORD_FILE", default=None), default=env("POSTGRES_PASSWORD", default=""))
    cfg: dict[str, Any] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": name,
        "USER": user,
        "PASSWORD": pwd,
        "HOST": host,
        "PORT": port,
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", default=60),
        "OPTIONS": {"connect_timeout": env.int("DB_CONNECT_TIMEOUT", default=5)},
    }

    if env.bool("DB_SSL_REQUIRED", default=False):
        cfg.setdefault("OPTIONS", {}).update({"sslmode": env("DB_SSLMODE", default="require")})
    return cfg


# def build_redis_url(db_env_name: str, default_db: str) -> str:
#     """
#     Compose a `redis://` URL from REDIS_* envs plus `REDIS_PASSWORD[_FILE]`.
#
#     Args:
#         db_env_name: Name of the env var carrying the logical Redis DB index
#                      (e.g., "REDIS_DB_BROKER").
#         default_db: Fallback DB index string to use when `db_env_name` is unset.
#
#     Returns:
#         A `redis://` or `redis://:password@host:port/db` connection URL.
#     """
#     host = env("REDIS_HOST", default="redis")
#     port = env("REDIS_PORT", default="6379")
#     db = env(db_env_name, default=default_db)
#     pwd = read_secret(
#         env("REDIS_PASSWORD_FILE", default=None), default=env("REDIS_PASSWORD", default="")
#     )
#     if pwd:
#         return f"redis://:{quote_plus(pwd)}@{host}:{port}/{db}"
#     return f"redis://{host}:{port}/{db}"

# ---------------------------------------------------------------------
# Core / Security
# ---------------------------------------------------------------------
DEBUG: bool = env.bool("DEBUG", default=True)

# Security key for cryptographic signing
SECRET_KEY: str = read_secret(
    env("DJANGO_SECRET_KEY_FILE", default=None),
    default=env("SECRET_KEY", default="dev-secret-key-change-me"),
)

# IMPORTANT: use list defaults, not strings
ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["*"])
CSRF_TRUSTED_ORIGINS: list[str] = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------
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
    "tsl_manager_app.apps.TslManagerAppConfig",
]

# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],  # Global templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------
# URL / WSGI / ASGI
# ---------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------
# Priority:
# 1) DATABASE_URL (convenient in dev)
# 2) DB_* + DB_PASSWORD_FILE (Docker secrets)
# 3) SQLite fallback
if env("DATABASE_URL", default=None):
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    if any(
        env(e, default=None)
        for e in [
            "DB_NAME",
            "DB_USER",
            "DB_HOST",
            "DB_PORT",
            "DB_PASSWORD_FILE",
            "POSTGRES_PASSWORD",
        ]
    ):
        DATABASES = {"default": build_postgres_dict_from_parts()}
    else:
        DATABASES = {"default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")}

# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = env("LANGUAGE_CODE", default="en")
TIME_ZONE = env("TZ", default="Europe/Warsaw")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", default="/code/media"))

# ---------------------------------------------------------------------
# DEFAULT FIELD CONFIGURATION
# ---------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# AUTHENTICATION REDIRECTS
# ---------------------------------------------------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "new_services"
LOGOUT_REDIRECT_URL = "greeting_view"

# ---------------------------------------------------------------------
# BOOTSTRAP 5 CONFIGURATION
# ---------------------------------------------------------------------
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
