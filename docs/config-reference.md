# Configuration reference

`honor.config.json` constitutes the entire portal. Every key is validated by Pydantic models (`extra="forbid"`), causing typos to fail at load time. The committed [`honor.schema.json`](https://github.com/Kein95/luonvuituoi-honor-roll/blob/main/honor.schema.json) provides editors with autocomplete capability; point your file to it:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/Kein95/luonvuituoi-honor-roll/main/honor.schema.json",
  "project": { /* … */ }
}
```

## Top-level keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `project` | object | ✓ | Display name, slug, locale, tagline, branding. |
| `competitions` | array | ✓ (≥1) | The competitions you publish (Demo Olympiad A, Demo Olympiad B, …). |
| `editions` | array | ✓ (≥1) | competition + year pairs you've run. |
| `medals` | object | ✓ (≥1) | Global medal registry: code → definition. |
| `data_mapping` | object | | Column-name mapping for ingest. |
| `display` | object | | UI layout + defaults. |
| `admin` | object | | Admin surface toggle + auth mode. |

## `project`

```json
"project": {
  "name": "LUONVUITUOI HONOR ROLL",
  "slug": "demo-honor",
  "locale": "vi",
  "tagline": "Vinh danh học sinh Việt Nam",
  "branding": { "primary_color": "#667eea", "accent_color": "#764ba2", "logo_url": null }
}
```

- `slug` must be lowercase kebab-case; it names the SQLite file (`data/<slug>.db`).
- `locale` is `"en"` or `"vi"`; selects the UI strings.
- `branding.logo_url` must start with `/`, `http://`, `https://`, or `data:image/` (XSS sink closed).

## `competitions[]`

```json
{
  "id": "demo-a",
  "name": "Demo Olympiad A",
  "name_vi": "Demo Olympiad A",
  "candidate_field": "sbd",
  "subjects": [
    { "code": "MATH", "name": "Mathematics", "name_vi": "Toán học" }
  ],
  "medals": ["GOLD", "SILVER", "BRONZE", "MERIT"]
}
```

- `id` is a URL-safe identifier `[A-Za-z0-9_-]+`.
- `medals` is uppercased + deduped on load; every entry **must** exist in the top-level `medals` registry (validated cross-field).

## `editions[]`

```json
{ "competition_id": "demo-a", "year": 2025, "label": "Demo Olympiad A 2025" }
```

- `competition_id` must reference a declared competition (validated cross-field).
- `(competition_id, year)` pairs must be unique, with one edition per competition per year.

## `medals`

```json
"medals": {
  "GOLD":   { "rank": 1, "label_en": "Gold Medal",   "label_vi": "Huy chương Vàng", "color": "#FFD700", "icon": "🥇" },
  "SILVER": { "rank": 2, "label_en": "Silver Medal", "label_vi": "Huy chương Bạc",  "color": "#C0C0C0", "icon": "🥈" }
}
```

- `rank` determines sort order (lower = more prestigious; ranks must be unique).
- `color` is a hex string used for the medal badge background.

## `data_mapping`

Maps your source file's headers to the logical fields. Defaults assume `candidate_no`, `name`, `grade`, `photo`, `school`, `rank`, `medal`, `subject` columns. `photo` is a URL (https, a site-relative `/path`, or a `data:` URI) shown as the student's avatar:

```json
"data_mapping": {
  "candidate_no_col": "candidate_no",
  "name_col": "name",
  "grade_col": "grade",
  "photo_col": "photo",
  "school_col": "school",
  "rank_col": "rank",
  "medal_col": "medal",
  "subject_col": "subject",
  "percentile_col": null
}
```

Set any optional column to `null` (or omit it) when your source doesn't have it.

## `display`

```json
"display": {
  "layout": "both",
  "show_rank": true,
  "show_percentile": false,
  "cards_per_row": 4,
  "default_competition": null,
  "default_year": null
}
```

- `layout`: `"cards"`, `"table"`, or `"both"`.
- `cards_per_row`: 1–8 (responsive grid collapses on mobile regardless).

## `admin`

```json
"admin": { "enabled": true, "auth_mode": "password" }
```

!!! warning "Admin auth scope"
    The v0.1 admin surface (`/admin` + `/api/admin/*`) has **no built-in session authentication**. Deployments that expose it publicly must gate it behind a reverse proxy (Basic Auth / OAuth / IP allowlist). See [`SECURITY.md`](https://github.com/Kein95/luonvuituoi-honor-roll/blob/main/SECURITY.md). Set `enabled: false` to disable the write surface entirely.
