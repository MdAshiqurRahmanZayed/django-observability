#!/bin/sh
set -e

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
except Exception as e:
    sys.exit(1)
" 2>/dev/null; do
  sleep 1
done
echo ">>> PostgreSQL is ready"

echo ">>> Running migrations..."
python manage.py migrate --noinput

echo ">>> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo ">>> Starting Gunicorn on 0.0.0.0:9000..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:9000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info
