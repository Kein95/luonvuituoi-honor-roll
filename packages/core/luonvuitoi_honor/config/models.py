"""Pydantic models for ``honor.config.json``.

Design rules (mirrors the sibling LUONVUITUOI-CERT config layer):
- Every field that has an obvious default carries one, so minimal configs are tiny.
- Cross-field invariants live in ``@model_validator`` hooks on :class:`HonorConfig`
  (e.g., every edition's ``competition_id`` must reference a declared competition;
  every competition's ``medals`` must exist in the global medal registry).
- Enums are declared as ``Literal`` unions so the exported JSON Schema lists valid
  values explicitly for editor autocomplete.

The honor-roll domain is simpler than the certificate domain: a single flat
``achievements`` table holds one row per award, and "editions" are just
competition+year metadata used for filtering and labelling. That keeps the
public listing query a single indexed SELECT rather than a fan-out across
per-round tables.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

LocaleCode = Literal["en", "vi"]
LayoutMode = Literal["cards", "table", "both"]
AdminAuthMode = Literal["password"]

_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
# Slug: lowercase kebab-case segments joined by single hyphens, no leading/trailing hyphen.
_SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Identifier used as a dict/URL key — letters/digits/_/- only, no path separators.
_IDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
# Medal/subject code — uppercase A-Z, digits and underscore, short.
_CODE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_SAFE_LOGO_SCHEMES = ("/", "http://", "https://", "data:image/")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Branding(_Strict):
    logo_url: str | None = None
    primary_color: str = "#667eea"
    accent_color: str = "#764ba2"

    @field_validator("primary_color", "accent_color")
    @classmethod
    def _hex(cls, v: str) -> str:
        if not _HEX_COLOR.match(v):
            raise ValueError(f"expected hex color (e.g. #667eea), got {v!r}")
        return v

    @field_validator("logo_url")
    @classmethod
    def _safe_scheme(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return v
        if not any(v.startswith(prefix) for prefix in _SAFE_LOGO_SCHEMES):
            raise ValueError(f"branding.logo_url must start with {list(_SAFE_LOGO_SCHEMES)}; got {v!r}")
        return v


class Project(_Strict):
    name: str = Field(min_length=1, max_length=120)
    name_en: str | None = Field(
        default=None, max_length=120, description="English project name (bilingual UI header)."
    )
    slug: str = Field(min_length=1, max_length=60)
    locale: LocaleCode = "vi"
    tagline: str | None = Field(default=None, max_length=160)
    tagline_en: str | None = Field(
        default=None, max_length=160, description="English tagline (bilingual UI)."
    )
    branding: Branding = Field(default_factory=Branding)

    @field_validator("slug")
    @classmethod
    def _slug(cls, v: str) -> str:
        if not _SLUG.match(v):
            raise ValueError(f"slug must be lowercase kebab-case, got {v!r}")
        return v


class Subject(_Strict):
    code: str = Field(min_length=1, max_length=20, description="Short code (e.g. MATH, ENGLISH).")
    name: str = Field(min_length=1, max_length=60)
    name_vi: str | None = Field(default=None, max_length=60)
    icon: str = Field(default="📚", max_length=8, description="Emoji shown next to the subject.")

    @field_validator("code")
    @classmethod
    def _code(cls, v: str) -> str:
        if not _CODE.match(v):
            raise ValueError(f"subject.code must be uppercase [A-Z0-9_] starting with a letter, got {v!r}")
        return v


class Competition(_Strict):
    id: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=80)
    name_vi: str | None = Field(default=None, max_length=80)
    candidate_field: str = Field(
        default="candidate_no",
        min_length=1,
        max_length=40,
        description="Logical name of the candidate identifier (sbd / candidate_no).",
    )
    subjects: list[Subject] = Field(default_factory=list)
    medals: list[str] = Field(min_length=1, description="Ordered medal codes this competition awards.")

    @field_validator("id")
    @classmethod
    def _ident(cls, v: str) -> str:
        if not _IDENT.match(v):
            raise ValueError(f"competition.id must match {_IDENT.pattern}, got {v!r}")
        return v

    @field_validator("medals")
    @classmethod
    def _medals_upper(cls, v: list[str]) -> list[str]:
        out: list[str] = []
        for m in v:
            m = m.strip().upper()
            if not m:
                raise ValueError("competition.medals entries must not be empty")
            out.append(m)
        if len(out) != len(set(out)):
            raise ValueError(f"competition.medals must be unique: {out}")
        return out


class Edition(_Strict):
    competition_id: str = Field(min_length=1, max_length=40)
    year: int = Field(ge=1900, le=2100)
    label: str = Field(min_length=1, max_length=160, description="Human label shown in the UI.")
    upcoming: bool = Field(
        default=False, description="Declared but no data yet — shown as a 'coming soon' note."
    )

    @field_validator("competition_id")
    @classmethod
    def _ident(cls, v: str) -> str:
        if not _IDENT.match(v):
            raise ValueError(f"edition.competition_id must match {_IDENT.pattern}, got {v!r}")
        return v


class Medal(_Strict):
    rank: int = Field(ge=1, description="Sort rank; lower = more prestigious.")
    label_en: str = Field(min_length=1, max_length=60)
    label_vi: str = Field(min_length=1, max_length=60)
    color: str = "#888888"
    icon: str = "🏅"

    @field_validator("color")
    @classmethod
    def _hex(cls, v: str) -> str:
        if not _HEX_COLOR.match(v):
            raise ValueError(f"expected hex color, got {v!r}")
        return v


class TeamAward(_Strict):
    """One team/group award type (e.g. Champion, Runner-up, Best)."""

    rank: int = Field(ge=1, description="Sort rank; lower = more prestigious.")
    label_en: str = Field(min_length=1, max_length=60)
    label_vi: str = Field(min_length=1, max_length=60)
    color: str = "#888888"
    icon: str = "🏆"

    @field_validator("color")
    @classmethod
    def _hex(cls, v: str) -> str:
        if not _HEX_COLOR.match(v):
            raise ValueError(f"expected hex color, got {v!r}")
        return v


class Display(_Strict):
    layout: LayoutMode = "both"
    show_rank: bool = True
    show_percentile: bool = False
    cards_per_row: int = Field(default=4, ge=1, le=8)
    default_competition: str | None = None
    default_year: int | None = None


class DataMapping(_Strict):
    """Column-name mapping used when ingesting achievement source files.

    Each field names the header the operator's CSV/Excel/JSON uses for that
    logical concept, so a renamed column only needs a config edit — no code change.
    """

    candidate_no_col: str = "candidate_no"
    name_col: str = "name"
    grade_col: str | None = "grade"
    photo_col: str | None = "photo"
    school_col: str | None = "school"
    rank_col: str | None = "rank"
    medal_col: str = "medal"
    subject_col: str | None = "subject"
    percentile_col: str | None = None
    competition_col: str | None = None
    year_col: str | None = None


class AdminConfig(_Strict):
    enabled: bool = True
    auth_mode: AdminAuthMode = "password"


class Contact(_Strict):
    """Optional public contact info shown in the footer."""

    email: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=160)
    repo_url: str | None = Field(
        default=None, max_length=200, description="Public source repo link shown in the footer."
    )

    @field_validator("repo_url")
    @classmethod
    def _repo_url(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith(("https://", "http://")):
            raise ValueError(f"contact.repo_url must be an http(s) URL, got {v!r}")
        return v


class HonorConfig(_Strict):
    """Root document for ``honor.config.json``. All handlers read from this."""

    project: Project
    competitions: list[Competition] = Field(min_length=1, max_length=50)
    editions: list[Edition] = Field(min_length=1, max_length=200)
    medals: dict[str, Medal] = Field(min_length=1, description="Global medal registry: code → definition.")
    data_mapping: DataMapping = Field(default_factory=DataMapping)
    display: Display = Field(default_factory=Display)
    admin: AdminConfig = Field(default_factory=AdminConfig)
    contact: Contact = Field(default_factory=Contact)
    team_awards: dict[str, TeamAward] = Field(
        default_factory=dict, description="Optional registry of team/group award types (code -> definition)."
    )

    @model_validator(mode="after")
    def _competition_ids_unique(self) -> HonorConfig:
        ids = [c.id for c in self.competitions]
        if len(ids) != len(set(ids)):
            raise ValueError("competitions[].id must be unique")
        return self

    @model_validator(mode="after")
    def _edition_refs_valid(self) -> HonorConfig:
        known = {c.id for c in self.competitions}
        for ed in self.editions:
            if ed.competition_id not in known:
                raise ValueError(
                    f"edition {ed.year} references unknown competition_id {ed.competition_id!r}; "
                    f"available: {sorted(known)}"
                )
        return self

    @model_validator(mode="after")
    def _editions_unique(self) -> HonorConfig:
        keys = [(e.competition_id, e.year) for e in self.editions]
        if len(keys) != len(set(keys)):
            raise ValueError("editions[] must be unique by (competition_id, year)")
        return self

    @model_validator(mode="after")
    def _competition_medals_registered(self) -> HonorConfig:
        registered = set(self.medals.keys())
        for c in self.competitions:
            missing = set(c.medals) - registered
            if missing:
                raise ValueError(
                    f"competition {c.id!r} lists medals not in the global medal registry: {sorted(missing)}"
                )
        return self

    @model_validator(mode="after")
    def _competition_subject_codes_unique(self) -> HonorConfig:
        for c in self.competitions:
            codes = [s.code for s in c.subjects]
            if len(codes) != len(set(codes)):
                raise ValueError(f"competition {c.id!r} has duplicate subject codes: {codes}")
        return self

    @model_validator(mode="after")
    def _medal_ranks_unique(self) -> HonorConfig:
        ranks = [m.rank for m in self.medals.values()]
        if len(ranks) != len(set(ranks)):
            raise ValueError(f"medal ranks must be unique: {ranks}")
        return self

    @model_validator(mode="after")
    def _registry_codes_safe(self) -> HonorConfig:
        """Medal/team-award codes are interpolated into SQL CASE clauses, so they
        must be safe identifiers (no quotes/spaces) — this closes any injection path."""
        for key in self.medals:
            if not _CODE.match(key):
                raise ValueError(f"medal registry code {key!r} must match {_CODE.pattern}")
        for key in self.team_awards:
            if not _CODE.match(key):
                raise ValueError(f"team_awards code {key!r} must match {_CODE.pattern}")
        return self
