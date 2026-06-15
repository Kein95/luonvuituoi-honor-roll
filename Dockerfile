FROM python:3.11-slim

# The honor roll is single-process by design (SQLite store, no KV backend),
# so WEB_CONCURRENCY stays at 1 unless you move the store to a shared host.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PROJECT_ROOT=/app/project \
    WEB_CONCURRENCY=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install engine + CLI + gunicorn. CLI pulls in luonvuitoi-honor transitively,
# so one install covers both.
COPY packages/core /app/_build/core
COPY packages/cli /app/_build/cli
RUN pip install /app/_build/core /app/_build/cli gunicorn && rm -rf /app/_build

# Placeholder so cold-starts don't crash before a volume is mounted.
RUN mkdir -p /app/project/data

# Real WSGI entrypoint committed to the repo.
COPY wsgi.py /app/wsgi.py

# Run as a non-root user.
RUN groupadd --system app && useradd --system --gid app --home /app --no-create-home app \
    && chown -R app:app /app
USER app

EXPOSE 8000
# /health is a cheap, dependency-free probe — no DB write, no rate-limit impact.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-1} --timeout 60 --access-logfile - wsgi:app"]
