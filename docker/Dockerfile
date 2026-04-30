FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r base.txt

COPY . .
RUN chmod +x docker/entrypoint.sh

EXPOSE 8000
CMD ["./docker/entrypoint.sh"]