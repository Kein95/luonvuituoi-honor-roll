# Troubleshooting

Common issues and solutions when setting up, running, or using LUONVUITUOI-HONOR ROLL.

## Installation & setup

### `lvt-honor` command not found

**Symptom:** Running `lvt-honor init` returns `command not found`.

**Cause:** The CLI package is not installed or not in your PATH.

**Fix:**

```bash
# Install the CLI from PyPI
pip install luonvuitoi-honor-cli

# Or from a local dev clone
cd packages/cli && pip install -e .

# Verify
lvt-honor --version
```

### Python version mismatch

**Symptom:** `lvt-honor` fails with `SyntaxError` or `TypeError` about type hints.

**Cause:** You're running Python < 3.10. The project requires Python 3.10+.

**Fix:**

```bash
python3 --version
# If < 3.10, upgrade or use a version manager (pyenv, asdf)
pyenv install 3.12
pyenv local 3.12
```

### Config validation fails on load

**Symptom:** `lvt-honor dev` returns `ValidationError: ...` and won't start.

**Cause:** Your `honor.config.json` has a typo or invalid structure.

**Fix:**

1. Open `honor.config.json` in a JSON editor (VS Code, Sublime, etc.).
2. Check for common errors:
   - Trailing commas in arrays or objects.
   - Missing required fields (`project`, `competitions`, `editions`, `medals`).
   - Medal codes in `competitions[].medals` that don't exist in the top-level `medals` registry.
   - `edition.competition_id` referencing a competition that doesn't exist.
3. Validate against the schema:

```bash
# Download the schema
curl -o honor.schema.json https://raw.githubusercontent.com/Kein95/luonvuituoi-honor-roll/main/honor.schema.json

# Validate (requires ajv-cli)
npm install -g ajv-cli
ajv validate -s honor.schema.json -d honor.config.json
```

## Running locally

### Port already in use

**Symptom:** `lvt-honor dev` fails with `Address already in use: ('127.0.0.1', 8000)`.

**Cause:** Another process is listening on port 8000.

**Fix:**

```bash
# Find what's using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>

# Or use a different port
lvt-honor dev --port 9000
```

### Database locked

**Symptom:** Importing data or viewing the page returns `database is locked`.

**Cause:** Another process (another `lvt-honor` instance or a stale Python process) has an exclusive lock on the database.

**Fix:**

```bash
# Kill any stray Python processes
pkill -f "lvt-honor dev"

# Or on Windows
taskkill /F /IM python.exe

# Retry
lvt-honor dev
```

### Import fails with "column not found"

**Symptom:** `lvt-honor import results.csv` returns `KeyError: 'expected_column_name'`.

**Cause:** Your CSV headers don't match the `data_mapping` in your config.

**Fix:**

1. Check the CSV headers:

```bash
head -1 results.csv
# Output: sbd, name, school, subject, medal, rank
```

2. Check the config:

```bash
grep -A 10 '"data_mapping"' honor.config.json
```

3. If headers don't match, either:
   - **Rename the CSV columns** to match the config, OR
   - **Update `data_mapping`** in the config to match the CSV.

Example:

```json
"data_mapping": {
  "candidate_no_col": "sbd",
  "name_col": "name",
  "school_col": "school",
  "subject_col": "subject",
  "medal_col": "medal",
  "rank_col": "rank"
}
```

## Browsing the portal

### Search returns no results, but I see students elsewhere

**Cause:** The search is working, but the student name was not imported or was imported with a different spelling.

**Fix:**

1. Check the filters on the home page; they may be narrowing the view.
2. Use the admin panel to verify the student is in the database:

```bash
sqlite3 data/honor.db "SELECT name, school, medal FROM achievements WHERE name LIKE '%nguyen%' LIMIT 5;"
```

3. If the student is in the database but search doesn't find them, check the name encoding (UTF-8 vs. Latin-1).

### Filters don't narrow the results

**Cause:** You've selected a filter, but the page still shows all students.

**Fix:**

1. Refresh the page.
2. Check that the filter value exists in the data:

```bash
# Check if the competition exists
sqlite3 data/honor.db "SELECT DISTINCT competition_id FROM achievements;"

# Check if the year has data
sqlite3 data/honor.db "SELECT DISTINCT year FROM achievements WHERE competition_id = 'demo-a';"
```

### Photos are broken (404 or blank)

**Cause:** The photo URLs in the import data are missing or incorrect.

**Fix:**

1. Check the `data_mapping` in the config; `photo_col` should point to the correct CSV column.
2. Verify photo URLs are absolute (start with `http://`, `https://`, or `data:image/`).
3. Check that the URLs are still valid:

```bash
curl -I "https://example.com/student-photo.jpg"
# Should return 200, not 404
```

4. If photos are optional, set `photo_col: null` in the config:

```json
"data_mapping": { "photo_col": null }
```

## Admin panel

### Admin button is missing

**Cause:** The admin surface is disabled (`admin.enabled: false`).

**Fix:**

Edit `honor.config.json` and set:

```json
"admin": { "enabled": true, "auth_mode": "password" }
```

Then restart the portal.

### Can't log in (password always wrong)

**Cause:** The `ADMIN_PASSWORD` environment variable is not set or incorrect.

**Fix:**

```bash
# Check if the variable is set
echo $ADMIN_PASSWORD

# If empty, set it
export ADMIN_PASSWORD="your-secure-password"

# Restart
lvt-honor dev
```

### Login works, but admin page is blank or broken

**Cause:** A JavaScript error or session cookie issue.

**Fix:**

1. Open browser DevTools (F12) and check the Console for errors.
2. Check the Network tab to determine if requests to `/api/admin/*` are returning 200.
3. Try clearing cookies and logging in again:

```bash
# In the browser console
document.cookie.split(";").forEach(c => {
  const eqPos = c.indexOf("=");
  const name = eqPos > -1 ? c.substr(0, eqPos).trim() : c.trim();
  document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
});
```

Then reload the page and log in again.

## Docker deployment

### Container exits immediately

**Symptom:** `docker compose up` shows the container exiting with code 1.

**Fix:**

```bash
# Check the logs
docker compose logs honor

# Common causes:
# - ADMIN_PASSWORD not set in .env
# - honor.config.json is invalid
# - project/data/ directory missing

# Verify
ls -la project/honor.config.json
grep ADMIN_PASSWORD .env
```

### `Permission denied` when mounting project

**Symptom:** Container runs but can't read `project/honor.config.json`.

**Fix:**

```bash
# Ensure the project directory is readable
chmod 755 project/
chmod 644 project/honor.config.json

# Restart
docker compose restart
```

### Database locked in Docker

**Cause:** Multiple worker processes racing on SQLite (common with `WEB_CONCURRENCY > 1`).

**Fix:**

In `docker-compose.yml`, ensure:

```yaml
environment:
  WEB_CONCURRENCY: 1
```

If you need to scale, migrate to PostgreSQL.

## Vercel deployment

### Build fails: `ModuleNotFoundError`

**Symptom:** Vercel build logs show `ModuleNotFoundError: No module named 'luonvuitoi_honor'`.

**Cause:** Dependencies are not installed during the build.

**Fix:**

Ensure your `requirements.txt` (or `pyproject.toml` with `poetry install`) is in the project root:

```bash
cat requirements.txt
# Should list: luonvuitoi-honor-cli, ...

# If missing, generate it
pip freeze > requirements.txt
git add requirements.txt
git commit -m "chore: add requirements.txt"
git push
```

### Admin surface returns 401

**Symptom:** Logging into `/admin` on Vercel always returns 401.

**Cause:** `ADMIN_PASSWORD` is not set in Vercel environment variables.

**Fix:**

1. Go to **Settings** > **Environment Variables** in the Vercel dashboard.
2. Add `ADMIN_PASSWORD` with your secure password.
3. Redeploy.

### Cold start is slow

**Symptom:** First request takes 3–5 seconds.

**Cause:** Serverless cold starts are normal. Python runtime initialization takes ~200ms, plus imports.

**Mitigation:**

- Use Vercel's **Concurrency** feature to keep the function warm.
- Consider using a more permanent hosting (Docker on Railway, Render, etc.).

## General debugging

### Enable debug logging

```bash
# Set the log level
export LOG_LEVEL=DEBUG
lvt-honor dev
```

### Inspect the database

```bash
# Open SQLite CLI
sqlite3 data/honor.db

# List tables
.tables

# Show schema
.schema achievements

# Count rows
SELECT COUNT(*) FROM achievements;

# Find data issues
SELECT * FROM achievements WHERE name LIKE '%unknown%' LIMIT 5;
```

### Check environment variables

```bash
# List all env vars the app sees
env | grep -E "ADMIN|SECRET|PUBLIC"

# Check a specific one
echo $ADMIN_PASSWORD
```

## Still stuck?

If none of these solutions work:

1. **Check the logs**: Review both application logs and system logs (`docker logs`, `vercel logs --follow`).
2. **Read the error message carefully**: It often hints at the root cause.
3. **Isolate the issue**: Determine whether the problem occurs during setup, import, browsing, or deployment.
4. **Search the GitHub issues**: Your problem may already be documented.
5. **Ask for help**: Open a GitHub Discussion or issue with the following information:
   - Python version (`python --version`)
   - OS and environment (Docker, Vercel, local dev)
   - Steps to reproduce
   - Full error message and logs
