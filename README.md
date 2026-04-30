# University Task Tracker

Pet-project for optimizing university business processes.

## Stack
Python, Django, DRF, PostgreSQL, Redis, Celery, Docker.

## Quick Start (Docker)
1. `cp .env.example .env`
2. `docker compose up -d --build`
3. Open `http://localhost/api/v1/docs/swagger/`

## Quick Start (Local)
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements/dev.txt`
3. `cp .env.example .env` (update DB_HOST to localhost)
4. `python manage.py migrate`
5. `python manage.py runserver`
6. `celery -A config worker -l info` (in separate terminal)