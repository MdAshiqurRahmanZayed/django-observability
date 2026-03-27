#!/bin/sh
set -e

mkdir -p /app/logs

# ── 1. Wait for PostgreSQL ────────────────────────────────────────────────────
echo ">>> Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
    )
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done
echo ">>> PostgreSQL is ready"

# ── 2. Migrate only if there are pending migrations ───────────────────────────
echo ">>> Checking for pending migrations..."
PENDING=$(python manage.py showmigrations --list 2>/dev/null | grep -c '\[ \]' || true)
if [ "$PENDING" -gt 0 ]; then
  echo ">>> Found ${PENDING} pending migration(s) — running migrate..."
  python manage.py migrate --noinput
else
  echo ">>> No pending migrations — skipping"
fi

# ── 3. collectstatic — admin panel only ───────────────────────────────────────
# Main site CSS/JS lives in site_static/ and is served directly by Nginx —
# no collectstatic needed for it. We still run collectstatic for Django admin.
# Only re-runs if admin source files have changed (checked via hash sentinel).
STATIC_SENTINEL="/app/static/.admin_checksum"
ADMIN_HASH=$(find /app/.venv -path "*/django/contrib/admin/static" -type d \
  -exec find {} -type f \; 2>/dev/null | sort | xargs md5sum 2>/dev/null | \
  md5sum | cut -d' ' -f1)

if [ -f "$STATIC_SENTINEL" ] && [ "$(cat $STATIC_SENTINEL)" = "$ADMIN_HASH" ]; then
  echo ">>> Admin static unchanged — skipping collectstatic"
else
  echo ">>> Running collectstatic for admin panel..."
  python manage.py collectstatic --noinput --clear
  echo "$ADMIN_HASH" > "$STATIC_SENTINEL"
  echo ">>> collectstatic done"
fi

# ── 4. Start Gunicorn ─────────────────────────────────────────────────────────
echo ">>> Starting Gunicorn on 0.0.0.0:9000..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:9000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info
