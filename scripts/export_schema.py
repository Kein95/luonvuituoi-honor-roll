#!/usr/bin/env python
"""Re-generate ``honor.schema.json`` from the live Pydantic models.

Run after editing ``packages/core/luonvuitoi_honor/config/models.py``::

    python scripts/export_schema.py

The ``test_schema_in_sync_with_models`` test fails if you forget, so editor
autocomplete never drifts from the actual validation rules.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running from a source checkout before pip install -e.
_REPO = Path(__file__).resolve().parent.parent
for candidate in (_REPO / "packages" / "core",):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from luonvuitoi_honor.config.models import HonorConfig  # noqa: E402


def main() -> int:
    schema = HonorConfig.model_json_schema()
    out = _REPO / "honor.schema.json"
    out.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"OK wrote {out} ({len(json.dumps(schema))} bytes, {len(schema.get('properties', {}))} top-level props)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
