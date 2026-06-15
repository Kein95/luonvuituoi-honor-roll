"""Vercel serverless entrypoint.

``@vercel/python`` mounts this as the WSGI app. Reads ``honor.config.json``
from the deployed project root so config travels with the code.
"""

import os
from pathlib import Path

from luonvuitoi_honor_cli.server import build_app

_ROOT = Path(os.environ.get("PROJECT_ROOT", ".")).resolve()
app = build_app(_ROOT / "honor.config.json", _ROOT)
