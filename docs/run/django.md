# Run Django App

Step-by-step guide to run the Django application.

---

## Prerequisites

- PostgreSQL running (`obs-postgres`)

---

## Start

### Option 1: Start All (Recommended)

```bash
# From project root
docker compose -f django_app/docker-compose.yml up -d
```

Django will start automatically after PostgreSQL is healthy.

### Option 2: Start Django Only

```bash
# Start PostgreSQL first
docker compose -f django_app/docker-compose.yml up -d obs-postgres

# Wait for healthy
sleep 5

# Then start Django
docker compose -f django_app/docker-compose.yml up -d obs-django
```

---

## Verify

```bash
# Check container
docker ps | grep obs-django

# Test metrics endpoint
curl http://localhost:9000/metrics | head -5

# Test web app
curl -I http://localhost/
```

???+ success "Expected Output"
    ```
    HTTP/1.1 200 OK
    Server: gunicorn
    Content-Type: text/html
    ```

---

## Access

| URL | Purpose |
|-----|---------|
| http://localhost | Web application (via Nginx) |
| http://localhost:9000 | Direct Django access |
| http://localhost:9000/metrics | Prometheus metrics |
| http://localhost:9000/admin/ | Django admin panel |

---

## Commands

### View Logs

```bash
docker logs -f obs-django
```

### Access Shell

```bash
docker exec -it obs-django /bin/sh
```

### Run Django Management Commands

```bash
# Check migrations
docker exec obs-django python manage.py showmigrations

# Run migrations
docker exec obs-django python manage.py migrate

# Create superuser
docker exec obs-django python manage.py createsuperuser

# Collect static files
docker exec obs-django python manage.py collectstatic --noinput
```

### Restart

```bash
docker compose -f django_app/docker-compose.yml restart obs-django
```

### Rebuild (After Code Changes)

```bash
docker compose -f django_app/docker-compose.yml up -d --build obs-django
```

---

## Configuration

Django reads from `django_app/.env`:

```bash
# Database
DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=obs-postgres
DB_PORT=5432

# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=*
```

---

## Troubleshooting

??? failure "Database connection error"
    ```bash
    # Check PostgreSQL is running
    docker ps | grep obs-postgres

    # Check PostgreSQL health
    docker inspect obs-postgres --format '{{.State.Health.Status}}'

    # Test connection from Django
    docker exec obs-django python manage.py dbshell -c "SELECT 1;"
    ```

??? failure "Container exits immediately"
    ```bash
    # Check logs
    docker logs obs-django

    # Check if port 9000 is in use
    lsof -i :9000
    ```

??? failure "Metrics not showing"
    ```bash
    # Test metrics endpoint
    curl http://localhost:9000/metrics

    # Check django_prometheus is installed
    docker exec obs-django pip list | grep prometheus
    ```

---

## Stop

```bash
docker compose -f django_app/docker-compose.yml stop obs-django
```
