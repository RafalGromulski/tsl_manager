"""
Production settings for the Django project.

This module extends the shared base settings (`base.py`) with configuration
suitable for a production environment:

- Debug disabled.
"""

from pathlib import Path

from .base import *  # noqa: F403, F401
from .base import SECRET_KEY, env

# ---------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------
# STATIC_ROOT = Path(env("STATIC_ROOT", default=BASE_DIR / "tsl_manager_app" / "static"))
STATIC_ROOT = Path(env("STATIC_ROOT", default="/code/static"))

# ---------------------------------------------------------------------
# CUSTOM PROJECT PATHS
# ---------------------------------------------------------------------
DATA_DIRECTORY: Path = Path(env("DATA_DIRECTORY", default="/code/tsl_downloads"))

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", default=31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)

# ---------------------------------------------------------------------
# Production security toggles
# ---------------------------------------------------------------------
if not DEBUG and ALLOWED_HOSTS == ["*"]:
    raise RuntimeError("Set ALLOWED_HOSTS explicitly for non-debug runs.")

# Auto-harden when DEBUG=False. You can still override via env in `prod.py`.
if not DEBUG:
    # Require proper secret in non-debug runs
    if not SECRET_KEY or SECRET_KEY == "dev-secret-key-change-me":
        raise RuntimeError("SECRET_KEY must be set when DEBUG is False.")
