#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings}

echo "Waiting for DB..."
while ! python manage.py check --database default >/dev/null 2>&1; do
  sleep 2
done

echo "Migrating..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput --clear

if [ "${CREATE_SUPERUSER:-false}" = "true" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput || true
fi

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers ${GUNICORN_WORKERS:-3} \
  --timeout ${GUNICORN_TIMEOUT:-120} \
  --access-logfile - \
  --error-logfile -