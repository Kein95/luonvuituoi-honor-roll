# Operations

How to run a LUONVUITUOI-HONOR ROLL deployment day-to-day: health probes, log surfaces, database choice, and the incident checklist.

## Health probe

```http
GET /health
```

Returns `{"ok": true}` with HTTP 200. The endpoint:

- Does **not** read the database.
- Does **not** write any state.
- Has no auth requirement.

Docker `HEALTHCHECK`, Kubernetes liveness, and load-balancer probes should all target this path.

## Logs

Everything flows through the stdlib `logging` module at `WARNING` and above. In Docker, those go to stdout and are captured by `docker logs`. On Vercel, use `vercel logs --follow` to stream them.

Loud messages worth alerting on:

| Logger | Message | Meaning |
|--------|---------|---------|
| `luonvuitoi_honor_cli.server.app` | `ADMIN_PASSWORD not set` | Admin login is disabled. Set the env var to enable it. |
| `luonvuitoi_honor.config` | `Cross-field validation failed` | The `honor.config.json` has a structural error (e.g., a medal referenced that doesn't exist). The portal will not start. |

Handled errors (404 searches, invalid filters) are not logged; they constitute normal traffic.

## Database

The portal stores achievements in an SQLite database at `data/<slug>.db` (path determined by your `honor.config.json#project.slug`).

### Data lifecycle

- **Seeding**: Use `lvt-honor seed` to generate fake data for local testing.
- **Importing**: Use `lvt-honor import <file>` to load achievements from CSV/Excel/JSON.
- **Deleting**: Use the admin panel (`/admin`) or direct SQLite commands.
- **Backing up**: Copy `data/<slug>.db` to a safe location.

### Querying the database

```bash
# List all achievements for a specific competition and year
sqlite3 data/honor.db "SELECT name, school, medal, subject_code FROM achievements WHERE competition_id = 'demo-a' AND year = 2025 ORDER BY name;"

# Count medals by tier
sqlite3 data/honor.db "SELECT medal, COUNT(*) FROM achievements WHERE year = 2025 GROUP BY medal;"

# Find duplicate students (same candidate_no, different names; data quality check)
sqlite3 data/honor.db "SELECT candidate_no, COUNT(DISTINCT name) FROM achievements GROUP BY candidate_no HAVING COUNT(DISTINCT name) > 1;"

# View admin activity (login success/failure, write actions)
sqlite3 data/honor.db "SELECT timestamp, action, ip FROM admin_activity ORDER BY timestamp DESC LIMIT 20;"
```

### Multi-process safety

By default, the portal uses SQLite's built-in locking. **If running multiple workers** (`WEB_CONCURRENCY > 1`), ensure:

- Single-file SQLite on a local filesystem (not NFS or network mount), OR
- Migrate to a PostgreSQL database (requires a schema adapter, not yet shipped).

The startup logs warn if you misconfigure this:

```
SQLite is not safe with 4 workers. Either drop to WEB_CONCURRENCY=1 or migrate to PostgreSQL.
```

## Admin credentials

### Setting the password

```bash
export ADMIN_PASSWORD="your-secure-password"
```

The password is not stored in the committed config; it is read from the environment only. This ensures the password is never accidentally committed to git.

### Changing the password

Restart the application with a new `ADMIN_PASSWORD`. Active sessions remain valid until the user closes their browser tab.

### Disabling the admin surface

Set `admin.enabled: false` in `honor.config.json`:

```json
"admin": { "enabled": false }
```

Requests to `/login`, `/admin`, and `/api/admin/*` return HTTP 404.

## Configuration hot-reload

Edit `honor.config.json` while the portal is running:

- **Docker:** update `project/honor.config.json` on the host, then `docker compose restart`.
- **Vercel:** update the config in your source code, redeploy, or use Vercel's environment variable override (if config is parameterized).
- **Local dev**: The portal reloads on each request; save the file to apply changes.

If the new config is invalid, the portal returns HTTP 500 with a validation error message.

## Monitoring checklist

- [ ] **Health probe passes**: `curl https://<portal>/health` returns 200.
- [ ] **Search works**: `/search?q=<name>` returns results or "not found", not errors.
- [ ] **Admin login works**: `/login` accepts the password and grants access to `/admin`.
- [ ] **Filters work**: Competition, year, medal, and subject dropdowns narrow results.
- [ ] **Import succeeds**: `lvt-honor import <file>` reports the row count.
- [ ] **Logs are clean**: `docker logs <container>` shows no `ERROR` or `CRITICAL` lines.
- [ ] **Database is reachable**: `sqlite3 data/honor.db ".tables"` lists the schema.

## Incident response

| Symptom | Diagnosis | Fix |
|---------|-----------|-----|
| `/health` returns 500 | Config is invalid or database is corrupt. | Check logs; validate `honor.config.json` with the schema. Restore database from backup if needed. |
| Admin login loops (password always wrong) | `ADMIN_PASSWORD` is not set or mistyped in env. | Verify the env var matches your password exactly. |
| Import reports "column not found" | CSV headers don't match `data_mapping` in config. | Check column names in the CSV and update `data_mapping` in the config. |
| Search returns no results, but students exist | Filters are too narrow; try resetting them with the **Reset** button. | Or the student name was imported with a typo; use the admin panel to verify the data. |
| Out of disk space | The SQLite database has grown too large, or temp files are accumulating. | Archive old data, delete temp files, or upgrade storage. |

## Scaling

- **Single-box deployment**: Set `WEB_CONCURRENCY=1` with SQLite on local disk. Suitable for up to approximately 50,000 students.
- **Multi-worker**: Migrate to PostgreSQL and set `WEB_CONCURRENCY=4` or higher. Suitable for any scale.

The query engine is I/O-bound rather than CPU-bound. Adding cores helps only if the database is remote and latency-bound. For most deployments, a single worker with fast local storage proves sufficient.
