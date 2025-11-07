"""
Development settings for the Django project.

This module extends the shared base settings (`base.py`) with configuration
suitable for local development:

- Debug mode enabled.
"""

from pathlib import Path

from .base import *  # noqa: F403, F401
from .base import BASE_DIR

# ---------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------
DEBUG = True

# ---------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------
STATICFILES_DIRS = [BASE_DIR / "tsl_manager_app" / "static"]

# ---------------------------------------------------------------------
# CUSTOM PROJECT PATHS
# ---------------------------------------------------------------------
DATA_DIRECTORY: Path = BASE_DIR / "send_to_db" / "data" / "data_1"
