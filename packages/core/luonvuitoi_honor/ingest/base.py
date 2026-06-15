"""Shared types for the ingest layer."""

from __future__ import annotations

from collections.abc import Iterable


class IngestError(Exception):
    """Raised when a source file cannot be read or parsed."""


class IngestResult:
    """Accumulator for ingest outcomes (inserted / skipped / warnings).

    Mirrors the sibling CERT toolkit's result shape so CLI output looks familiar.
    """

    __slots__ = ("rows_inserted", "rows_skipped", "rows_updated", "_warnings")

    def __init__(self) -> None:
        self.rows_inserted: int = 0
        self.rows_skipped: int = 0
        self.rows_updated: int = 0
        self._warnings: list[str] = []

    def warn(self, msg: str) -> None:
        self._warnings.append(msg)

    @property
    def warnings(self) -> list[str]:
        return list(self._warnings)

    def summary(self) -> str:
        parts = [f"inserted={self.rows_inserted}", f"skipped={self.rows_skipped}"]
        if self.rows_updated:
            parts.append(f"updated={self.rows_updated}")
        if self._warnings:
            parts.append(f"warnings={len(self._warnings)}")
        return ", ".join(parts)


SourceRow = dict[str, object]
SourceRows = Iterable[SourceRow]
