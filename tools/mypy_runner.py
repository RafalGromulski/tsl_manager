"""
Run `mypy` for a Django repository with predictable paths and settings.

This script locates the Django project directory that contains
``config/settings/dev.py``, amends ``PYTHONPATH`` to include that directory,
ensures ``DJANGO_SETTINGS_MODULE=config.settings.dev`` is set (if absent),
and then executes ``mypy`` from the repository root so that file/include/exclude
patterns in ``pyproject.toml`` are interpreted relative to the repo root.

Discovery strategy
------------------
1) Fast checks in:
   - ``<repo_root>/``
   - ``<repo_root>/django_project/``
2) Fallback scan (skipping common virtualenv/cache dirs such as
   ``.git``, ``.venv``, ``venv``, ``__pycache__``, ``.mypy_cache``,
   ``.pytest_cache``) to find ``config/settings/dev.py``.
   The project directory is taken as the parent of ``config``
   (i.e., ``.../config/settings/dev.py -> .../``).
3) If multiple candidates exist, the shortest path (highest in the tree)
   is chosen.

Environment
-----------
- ``PYTHONPATH`` is prefixed with the discovered project directory.
- ``DJANGO_SETTINGS_MODULE`` defaults to ``config.settings.dev`` if not set.

Mypy configuration
------------------
All CLI arguments are forwarded to ``mypy``. If ``--config-file`` is not
provided (as a separate flag or ``--config-file=...``), the script injects:
``--config-file <repo_root>/pyproject.toml`` (if that file exists).

Working directory
-----------------
``mypy`` is executed with ``cwd=<repo_root>`` to ensure patterns in
``pyproject.toml`` apply relative to the repository root.

Exit status
-----------
- ``0``: mypy completed successfully.
- ``1``: mypy reported type errors (standard mypy behavior).
- ``2``: no directory containing ``config/settings/dev.py`` was found.
- ``3``: failed to execute ``mypy`` (e.g., not installed).

Examples
--------
From anywhere inside the repo:

   code-block:: bash

   python tools/mypy_runner.py
   python tools/mypy_runner.py --strict
   python tools/mypy_runner.py --package my_app
   python tools/mypy_runner.py --config-file path/to/custom_pyproject.toml

Requirements
------------
- ``mypy`` available on ``PATH``.
- ``pyproject.toml`` at the repo root (unless you pass ``--config-file``).
- A Django settings module at ``config/settings/dev.py``.

Notes
-----
- The script does not overwrite an existing ``DJANGO_SETTINGS_MODULE``.
- When multiple ``config/settings/dev.py`` exist, the highest-level match wins.
"""

import os
import shlex
import subprocess
import sys
from pathlib import Path

EXIT_NOT_FOUND = 2
EXIT_EXEC_FAILED = 3


def find_project_dir(repo_root: Path) -> Path | None:
    """
    Return the project directory from which ``import config.settings.dev`` works.

    The directory must *contain* ``config/settings/dev.py``. For example, for:
        <repo_root>/django_project/config/settings/dev.py
    this returns:
        <repo_root>/django_project
    """
    candidates: list[Path] = []

    # 1) Fast checks: repo_root, repo_root/django_project
    for p in (repo_root, repo_root / "django_project"):
        if (p / "config" / "settings" / "dev.py").is_file():
            return p

    # 2) Fallback: scan, ignoring common caches/venvs
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".tox",
        "node_modules",
    }
    bases = [repo_root] + [d for d in repo_root.iterdir() if d.is_dir() and d.name not in skip_dirs]
    for base in bases:
        for dev_path in base.rglob("config/settings/dev.py"):
            project_dir = dev_path.parents[2]  # .../config/settings/dev.py -> .../
            if (project_dir / "config").is_dir():
                candidates.append(project_dir)

    # Pick the shortest path (highest in the tree)
    if candidates:
        return min(candidates, key=lambda x: len(str(x)))
    return None


def _has_config_flag(args: list[str]) -> bool:
    """Return True if args already contain a --config-file option."""
    for a in args:
        if a == "--config-file" or a.startswith("--config-file="):
            return True
    return False


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]  # tools/ -> <repo_root>
    project_dir = find_project_dir(repo_root)
    if project_dir is None:
        print(
            "ERROR: Could not find a directory containing 'config/settings/dev.py' in this repository.",
            file=sys.stderr,
        )
        print(
            "Make sure you have either <repo>/config/... or <repo>/django_project/config/...",
            file=sys.stderr,
        )
        return EXIT_NOT_FOUND

    # 1) PYTHONPATH: prepend the project directory
    current = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = str(project_dir) if not current else str(project_dir) + os.pathsep + current

    # 2) Set a safe default for Django settings (plugin still reads from pyproject)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

    # 3) Ensure mypy reads the repo's pyproject.toml unless the user overrides it
    args = sys.argv[1:]
    if not _has_config_flag(args):
        default_cfg = repo_root / "pyproject.toml"
        if default_cfg.is_file():
            args = ["--config-file", str(default_cfg), *args]

    # 4) Run mypy with CWD=repo_root so patterns in pyproject resolve properly
    cmd = ["mypy", *args]
    try:
        return subprocess.call(cmd, cwd=str(repo_root))
    except FileNotFoundError:
        print(
            "ERROR: 'mypy' not found on PATH. Install it (e.g., 'pip install mypy') and try again.",
            file=sys.stderr,
        )
        print(f"Tried command: {shlex.join(cmd)}", file=sys.stderr)
        return EXIT_EXEC_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
