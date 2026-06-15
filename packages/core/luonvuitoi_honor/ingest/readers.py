"""Source readers: CSV / Excel / JSON → list[dict].

Each reader returns a list of row dicts keyed by the source file's headers.
The orchestrator then projects those onto the config's ``data_mapping`` so a
renamed column only needs a config edit.
"""

from __future__ import annotations

import contextlib
import csv
import json
from pathlib import Path
from typing import Any

from luonvuitoi_honor.ingest.base import IngestError, SourceRow


def _coerce_cell(v: Any) -> object:
    """Normalise a cell to a JSON-serialisable scalar (str/int/float/None)."""
    if v is None:
        return None
    # pandas/numpy scalar wrappers → native
    if hasattr(v, "item"):
        with contextlib.suppress(Exception):  # pragma: no cover — defensive
            v = v.item()
    if isinstance(v, float) and v.is_integer():
        # keep ranks/years clean ints when the source stored them as floats
        return int(v)
    return v


def read_csv(path: str | Path, *, header_row: int = 0) -> list[SourceRow]:
    """Read a CSV into row dicts, honouring a 0-indexed header row."""
    p = Path(path)
    if not p.exists():
        raise IngestError(f"CSV file not found: {p}")
    try:
        with p.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
    except UnicodeDecodeError:
        # fall back to the platform default for legacy Vietnamese files
        with p.open(encoding="utf-8", errors="replace", newline="") as fh:
            rows = list(csv.reader(fh))
    if not rows:
        raise IngestError(f"CSV file is empty: {p}")
    if header_row >= len(rows):
        raise IngestError(f"header_row {header_row} is past end of file ({p})")
    header = [str(h).strip() for h in rows[header_row]]
    out: list[SourceRow] = []
    for r in rows[header_row + 1 :]:
        if not any(str(c).strip() for c in r):
            continue  # skip blank lines
        row: SourceRow = {}
        for i, cell in enumerate(r):
            key = header[i] if i < len(header) else f"col_{i}"
            row[key] = _coerce_cell(cell)
        out.append(row)
    return out


def read_excel(path: str | Path, *, sheet: int | str = 0, header_row: int = 0) -> list[SourceRow]:
    """Read an Excel sheet into row dicts using the given header row index."""
    try:
        import pandas as pd
    except ImportError as e:  # pragma: no cover
        raise IngestError("pandas/openpyxl is required to read .xlsx files") from e
    p = Path(path)
    if not p.exists():
        raise IngestError(f"Excel file not found: {p}")
    try:
        df = pd.read_excel(p, sheet_name=sheet, header=header_row, dtype=object)
    except Exception as e:  # noqa: BLE001 — surface a readable message
        raise IngestError(f"failed to read Excel ({p}): {e}") from e
    df = df.dropna(how="all")
    out: list[SourceRow] = []
    for rec in df.to_dict(orient="records"):
        out.append({str(k).strip(): _coerce_cell(v) for k, v in rec.items()})
    return out


def read_json(path: str | Path) -> list[SourceRow]:
    """Read a JSON file that is either a list of objects, or ``{year: [...]}``."""
    p = Path(path)
    if not p.exists():
        raise IngestError(f"JSON file not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise IngestError(f"invalid JSON ({p}): {e.msg} at line {e.lineno}") from e
    if isinstance(raw, list):
        if not all(isinstance(item, dict) for item in raw):
            raise IngestError(f"JSON list must contain objects ({p})")
        return [{str(k): _coerce_cell(v) for k, v in item.items()} for item in raw]
    if isinstance(raw, dict):
        out: list[SourceRow] = []
        for key, val in raw.items():
            if isinstance(val, list) and all(isinstance(i, dict) for i in val):
                for item in val:
                    row = {str(k): _coerce_cell(v) for k, v in item.items()}
                    row.setdefault("year", key)
                    out.append(row)
        if out:
            return out
    raise IngestError(
        f"JSON must be a list of objects or {{year: [objects]}} ({p}); got {type(raw).__name__}"
    )


def read_teams_file(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSON list of team objects.

    Shape: ``[{"name", "award", "subject", "category", "members": [{"name","grade","school"}]}]``.
    """
    p = Path(path)
    if not p.exists():
        raise IngestError(f"teams file not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise IngestError(f"invalid JSON ({p}): {e.msg} at line {e.lineno}") from e
    if not isinstance(raw, list) or not all(isinstance(x, dict) for x in raw):
        raise IngestError(f"teams file must be a JSON list of team objects ({p})")
    return raw


def read_file(path: str | Path, *, header_row: int = 0) -> list[SourceRow]:
    """Dispatch on file suffix to the right reader."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return read_csv(path, header_row=header_row)
    if suffix in {".xlsx", ".xlsm"}:
        return read_excel(path, header_row=header_row)
    if suffix == ".json":
        return read_json(path)
    raise IngestError(f"unsupported file type {suffix!r}: {path}")
