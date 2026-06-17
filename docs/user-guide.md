# User guide

How to use the honor roll portal: browse the gallery, search for students, view the hall of fame, and manage teams. If you are a developer deploying the portal, start at [quickstart.md](quickstart.md) instead.

## Who reads this

- **Visitors** (students, parents, prospective employers): See section [Browsing the honor roll](#browsing-the-honor-roll).
- **Operators** (competition staff, training admins): See section [Admin panel](#admin-panel).

## Browsing the honor roll

URL: `https://<your-portal>/`

### Filter by competition, year, medal, and subject

The honor roll displays all achievements by default. Use the filter dropdowns to narrow the view:

1. **Competition**: Select which olympiad or contest to view.
2. **Year**: Select the year or season.
3. **Medal**: Filter by award tier (Gold, Silver, Bronze, Merit, or custom tiers).
4. **Subject**: If the competition tracks subjects (MATH, ENGLISH, etc.), filter by subject.

Click **Reset** to clear all filters and show all records.

### View layout

The `display.layout` setting controls how results are shown:

- **Cards**: Gallery view with student photo, name, school, rank, and medal.
- **Table**: Dense tabular view showing all columns at once.
- **Both**: Tabs to switch between the two views.

## Search page

URL: `https://<your-portal>/search`

Find students by name using accent-tolerant matching. The search engine:

- Strips diacritics (`Nguyễn` matches `Nguyen`).
- Searches first name + surname.
- Returns all matches across all competitions and years.

Useful for visitors looking up a specific student or verifying their name appears in the roll.

## Hall of fame

URL: `https://<your-portal>/hall-of-fame`

A prestige ranking of top achievers. The hall shows:

- Students with the most prestigious medals (sorted by medal rank, then by competition prominence).
- An optional "all-time champion" or "lifetime achievement" view if your config defines it.
- School and competition badges.

The exact criteria depend on your `hall_of_fame` config section (future enhancement).

## Teams page

URL: `https://<your-portal>/teams`

If `team_awards` is configured in your `honor.config.json`, this page displays team/group accolades:

- Team name and photo (if provided).
- Award tier (Champion, Runner-up, Best Team, etc.).
- Member list (if included in the import data).
- School affiliation.

## Admin panel

URL: `https://<your-portal>/admin`

Access requires a password. The admin surface lets you:

- **Add achievements**: Upload a CSV/Excel/JSON file to ingest new student records.
- **Delete achievements**: Remove incorrect entries.
- **View stats**: Total students, medals per tier, competitions, and years.
- **Manage config**: Edit `honor.config.json` via the web UI (planned; currently via CLI).

### Login

1. Navigate to `/login`.
2. Enter the admin password (set via `ADMIN_PASSWORD` environment variable).
3. Click **Sign in**. Your session is valid for the browser tab; closing it logs you out.

### Adding achievements

1. Go to **Admin** > **Import data**.
2. Upload a CSV or Excel file with student records.
3. Specify the competition and year.
4. Choose **Append** (add new rows) or **Replace** (clear the year's data first).
5. Review the import summary: number of rows ingested, validation errors.

The import uses the `data_mapping` in your config to match column headers. If a column is missing or misnamed, the import will report an error.

### Deleting an achievement

1. Search for the student by competition, year, medal, or subject filter.
2. Find the row in the result.
3. Click the **Delete** button.
4. Confirm the deletion.

The row is removed immediately; the original import file is not affected.

### Viewing statistics

Navigate to **Admin** > **Stats** to see:

- Total unique students.
- Medal distribution (how many Gold, Silver, Bronze).
- Competitions published.
- Years with data.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Student not found" but I see them elsewhere | Check the filter settings (competition, year, subject). The search page searches across all records; the homepage filters by your current selections. |
| Search is too strict | Search strips diacritics; `Nguyễn` and `Nguyen` are equivalent. Check spelling; middle names matter. |
| Admin button is missing | The admin surface is disabled (`admin.enabled: false`). Contact the site operator. |
| Can't log in to admin | Verify the password is correct. The admin password is set via `ADMIN_PASSWORD` at deployment time, not in the config. |
| Import fails with "column not found" | Check your CSV headers match the `data_mapping` in your `honor.config.json`. |
