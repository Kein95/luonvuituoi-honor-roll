# Quickstart

## 1. Install

From a clone of the repo:

```bash
git clone https://github.com/Kein95/luonvuituoi-honor-roll
cd luonvuituoi-honor-roll
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ./packages/core -e ./packages/cli
```

## 2. Scaffold a project

```bash
lvt-honor init my-awards --name "My Awards" --slug my-awards --locale vi
cd my-awards
```

This writes `honor.config.json`, `api/index.py`, `requirements.txt`, and a `README.md`.

## 3. Prepare your results

Your source file can be CSV, Excel, or JSON. The columns it uses are mapped through `data_mapping` in the config, so a renamed column only needs a config edit. The minimum: a `name` and a `medal` column.

=== "CSV"

    ```csv
    name,school,subject,medal,rank,candidate_no
    X,School,MATHS,Gold,2,S001
    Y,School,ENGLISH,Silver,8,S002
    ```

=== "JSON"

    ```json
    [
      {"name": "X", "school": "School", "subject": "MATH", "medal": "GOLD", "rank": "2"},
      {"name": "Y", "school": "School", "subject": "ENGLISH", "medal": "SILVER", "rank": "8"}
    ]
    ```

!!! tip "Subject + medal normalisation"
    Subjects are uppercased (`Maths` → `MATHS`); medals are uppercased and must exist in the global medal registry (`gold` → `GOLD`). Rows without a name or a recognised medal are skipped (with a warning).

## 4. Import

```bash
lvt-honor import results.csv --competition demo-a --year 2025 --replace
```

`--replace` deletes that edition's existing rows first, so re-imports are idempotent.

## 5. Run

```bash
lvt-honor dev          # → http://127.0.0.1:5000
```

Open the portal, the `/search` page, and `/admin` in your browser.

## 6. (Optional) Seed fake data

To see the UI with data before your real results are ready:

```bash
lvt-honor seed --count 60
```

## Next steps

- [:material-cog: Configuration reference](config-reference.md): Every `honor.config.json` key explained.
- [:material-sitemap: Architecture](architecture.md): How the layers fit together.
- [:material-cloud: Deploy](deploy-vercel.md): Deploy to Vercel or Docker.
