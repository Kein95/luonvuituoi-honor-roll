"""WSGI entrypoint for container/serverless deploys.

Gunicorn targets ``wsgi:app`` in the Dockerfile CMD. Vercel picks this up via
``@vercel/python``. Reads ``PROJECT_ROOT`` (default ``/app/project``) for the
bind-mounted config + data directory.
"""

from __future__ import annotations

import os
from pathlib import Path

from luonvuitoi_honor_cli.server import build_app

_ROOT = Path(os.environ.get("PROJECT_ROOT", "/app/project")).resolve()
app = build_app(_ROOT / "honor.config.json", _ROOT)
