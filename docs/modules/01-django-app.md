# Django Application

## Overview

The Django Application is the core of this observability stack. It is a Python Django web application that serves as the primary application being monitored. It exposes metrics for Prometheus to scrape and generates logs that are shipped to Loki via Promtail.

## Description

This Django application is a Todo application that demonstrates modern observability practices. It is instrumented with:

- **Prometheus Metrics**: Via `django_prometheus` library for automatic metrics collection
- **Structured JSON Logging**: For log aggregation with Loki
- **PostgreSQL Database**: For persistent data storage
- **Sentry Integration**: For error tracking and performance monitoring

The application serves as a practical example of how to integrate observability into a Python Django application.

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY STACK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────────┐                                                         │
│    │   Django     │ ◀─── (1) Serves application                             │
│    │  Application │ ◀─── (2) Exposes /metrics endpoint                      │
│    │              │ ◀─── (3) Writes JSON logs to file                       │
│    └──────┬───────┘                                                         │
│           │                                                                 │
│           │ (2) GET /metrics         ┌──────────────┐                       │
│           ├─────────────────────────▶│  Prometheus  │                       │
│           │                          │  (scrape)    │                       │
│           │                          └──────────────┘                       │
│           │                                 │                               │
│           │ (3) Log files                   │ (4) Alert rules               │
│           ▼                                 ▼                               │
│    ┌──────────────┐                  ┌──────────────┐                       │
│    │   Promtail   │ ────────────────▶│Alertmanager │                        │
│    │  (tail logs) │                  │  (alerts)    │                       │
│    └──────┬───────┘                  └──────────────┘                       │
│           │                                                                 │
│           │ (3) POST /loki/api/v1/push                                      │
│           ▼                                                                 │
│    ┌──────────────┐                  ┌──────────────┐                       │
│    │     Loki     │ ◀─────────────── │   Grafana    │                       │
│    │  (logs)      │                  │  (UI)        │                       │
│    └──────────────┘                  └──────────────┘                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Django | 5.x |
| Metrics | django_prometheus | Latest |
| Logging | pythonjsonlogger | Latest |
| Error Tracking | Sentry SDK | Latest |
| WSGI Server | Gunicorn | Latest |
| Database | PostgreSQL | 16 |
| Python | Python | 3.12 |

## Architecture Diagram

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DJANGO APP ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Django Application                          │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐   │    │
│  │  │   Views     │  │   Models    │  │   Forms     │  │  Admin    │   │    │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘   │    │
│  │         │                │                │               │         │    │
│  │         └────────────────┼────────────────┼───────────────┘         │    │
│  │                          │                │                         │    │
│  │  ┌───────────────────────┴────────────────┴─────────────────────┐   │    │
│  │  │                    Django ORM                                │   │    │
│  │  └───────────────────────┬────────────────┬─────────────────────┘   │    │
│  │                          │                │                         │    │
│  │              ┌──────────┴────┐   ┌────────┴────────┐                │    │
│  │              │  PostgreSQL   │   │  JSON Logging   │                │    │
│  │              │  Database     │   │  /app/logs/     │                │    │
│  │              └───────────────┘   └────────┬────────┘                │    │
│  │                                           │                         │    │
│  │                    ┌──────────────────────┘                         │    │
│  │                    │                                                │    │
│  │  ┌─────────────────┴────────────────────────────────────────────-─-┐│    │
│  │  │              Middleware Stack                                   ││    │
│  │  │  ┌─────────────────────────────────────────────────────────----┐││    │
│  │  │  │ PrometheusBeforeMiddleware → ... → PrometheusAfterMiddleware│││    |
│  │  │  └────────────────────────────────────────────────────────----─┘││    │
│  │  └─────────────────────────────────────────────────────────────----┘|    │
│  │                                                                     │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                    Exposed Endpoints                          │  │    │
│  │  │  /metrics  /admin  /todo/  /api/  /static  /media             │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Docker Configuration

### docker-compose.yml

```yaml
# Django Application
obs-django:
  image: django-observability:latest    # Custom built Docker image
  container_name: obs-django
  build:
    context: .                          # Build from current directory
    dockerfile: Dockerfile
  restart: on-failure                   # Restart if container crashes
  ports:
    - "9000:9000"                       # Expose Gunicorn port
  volumes:
    - static_volume:/app/staticfiles    # Django static files
    - media_volume:/app/mediafiles      # User uploaded files
    - logs_volume:/app/logs             # Application logs (shared with Promtail)
  env_file:
    - .env                              # Load environment variables
  depends_on:
    obs-postgres:
      condition: service_healthy
  networks:
    - app_network
    - observability_network
```

### Key Settings

| Setting | Value | Description |
|---------|-------|-------------|
| `image` | `django-observability:latest` | Custom built Docker image |
| `ports` | `9000:9000` | Host:Container port mapping |
| `restart` | `on-failure` | Auto-restart on crash |
| `depends_on` | `obs-postgres` | Wait for database to be healthy |

## Network Access

### Internal Access (Within Docker Network)

| Service | Hostname | Port | Protocol |
|---------|----------|------|----------|
| Django | `obs-django` | 9000 | HTTP |

### External Access (From Host)

| Service | URL | Port |
|----------|-----|------|
| Django | http://localhost | 80 (via nginx) |
| Django Direct | http://localhost | 9000 |

### Networks Connected

```
┌─────────────────────────────────────────────┐
│         app_network                         │
│  ┌─────────────────────────────────────┐    │
│  │  obs-django  ◀───▶  obs-postgres    │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    observability_network                    │
│  ┌─────────────────────────────────────┐    │
│  │  obs-django  ◀───▶  Prometheus      │    │
│  │              ◀───▶  Promtail        │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

## Data Flow

### Metrics Flow

```
1. HTTP Request arrives at Django
        │
        ▼
2. PrometheusBeforeMiddleware starts timer
        │
        ▼
3. Request is processed by views/models
        │
        ▼
4. Django ORM queries PostgreSQL
        │
        ▼
5. PrometheusAfterMiddleware records:
   - Request duration
   - HTTP status code
   - HTTP method
   - View name
   - Database query duration
        │
        ▼
6. Prometheus scrapes /metrics endpoint
   GET http://obs-django:9000/metrics
        │
        ▼
7. Metrics stored in Prometheus TSDB
```

### Logging Flow

> **Note**: Log pushing to Loki is handled automatically by Promtail. You don't need to do anything manually!

```
Django writes JSON → Promtail tails file → Promtail pushes to Loki → Grafana queries
```

**Simple Flow:**
1. Django logs to `/app/logs/django.log` (JSON format)
2. Promtail tails the file automatically
3. Promtail pushes to Loki via `POST /loki/api/v1/push`
4. Query logs in Grafana

**You just call `logger.info("message")` - everything else is automatic!**

## Useful Commands

### Container Management

```bash
# View running container
docker ps | grep obs-django

# Restart Django container
docker compose -f django_app/docker-compose.yml restart obs-django

# Stop Django container
docker compose -f django_app/docker-compose.yml stop obs-django

# Start Django container
docker compose -f django_app/docker-compose.yml start obs-django

# Rebuild and start
docker compose -f django_app/docker-compose.yml up -d --build obs-django
```

### Shell Access

```bash
# Access container shell
docker exec -it obs-django /bin/sh

# Run Django management command
docker exec obs-django python manage.py showmigrations
docker exec obs-django python manage.py migrate
docker exec obs-django python manage.py createsuperuser
```

### Process Inspection

```bash
# View running processes
docker exec obs-django ps aux

# View Gunicorn master process
docker exec obs-django ps aux | grep gunicorn

# View thread count
docker exec obs-django ps -eLf | grep gunicorn | wc -l
```

### Network Inspection

```bash
# Check listening ports
docker exec obs-django netstat -tlnp
# OR
docker exec obs-django ss -tlnp

# Test internal connectivity
docker exec obs-django wget -qO- http://127.0.0.1:9000/metrics

# Check network connections
docker exec obs-django netstat -an
```

### Resource Usage

```bash
# View container resource usage
docker stats obs-django

# View container resource limits
docker inspect obs-django --format '{{json .HostConfig}}' | jq

# View disk usage
docker exec obs-django df -h

# View memory usage
docker exec obs-django free -h
```

## Expected Output

### Docker Stats Output

```
CONTAINER ID   NAME          CPU %   MEM USAGE / LIMIT     MEM %   NET I/O           BLOCK I/O         PIDS
abc123def456   obs-django    2.35%   256MiB / 512MiB       50.00%  1.23MB / 567KB    12.3MB / 4.19MB   12
```

### Metrics Endpoint Sample

```bash
$ curl http://localhost:9000/metrics

# HELP django_http_requests_total Total number of HTTP requests
# TYPE django_http_requests_total counter
django_http_requests_total{method="GET",status="200",view="todo_list"} 1234.0
django_http_requests_total{method="POST",status="302",view="todo_create"} 56.0

# HELP django_http_requests_latency_seconds HTTP request latency in seconds
# TYPE django_http_requests_latency_seconds histogram
django_http_requests_latency_seconds_bucket{le="0.005",method="GET",status="200",view="todo_list"} 890.0
django_http_requests_latency_seconds_bucket{le="0.01",method="GET",status="200",view="todo_list"} 1100.0

# HELP django_db_query_duration_seconds Database query duration in seconds
# TYPE django_db_query_duration_seconds histogram
django_db_query_duration_seconds_bucket{le="0.001",alias="default"} 5678.0
```

### Log File Sample

```json
{"asctime": "2026-03-15T10:30:45", "levelname": "INFO", "name": "django", "message": "GET /todo/ 200"}
{"asctime": "2026-03-15T10:30:46", "levelname": "DEBUG", "name": "django.db.backends", "message": "(0.005) SELECT ...", "duration": 0.005}
{"asctime": "2026-03-15T10:31:00", "levelname": "ERROR", "name": "todo.views", "message": "Something went wrong"}
```

## API Endpoints

### Prometheus Metrics

```bash
# Get all metrics
curl http://localhost:9000/metrics

# Get only Django-specific metrics
curl http://localhost:9000/metrics | grep "^django_"

# Get database metrics
curl http://localhost:9000/metrics | grep "^django_db"
```

### Application Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/admin/` | GET | Django admin panel |
| `/todo/` | GET | Todo list view |
| `/todo/add/` | GET/POST | Add todo |
| `/todo/<id>/` | GET/PUT/DELETE | Manage todo |
| `/accounts/login/` | GET/POST | User login |
| `/metrics` | GET | Prometheus metrics |

### Testing Endpoints

```bash
# Test home page
curl -I http://localhost:9000/

# Test admin
curl -I http://localhost:9000/admin/

# Test metrics endpoint
curl -I http://localhost:9000/metrics
```

## Health Checks

### Method 1: HTTP Check

```bash
# Check if Django is responding
curl -f http://localhost:9000/ || echo "Django is down"

# Check metrics endpoint
curl -f http://localhost:9000/metrics | head -5
```

### Method 2: Process Check

```bash
# Check if Gunicorn is running
docker exec obs-django pgrep -f gunicorn

# Expected output: process IDs (e.g., "1\n15\n16\n17")
```

### Method 3: Database Connection

```bash
# Check database connection
docker exec obs-django python manage.py dbshell -c "SELECT 1;"

# Check migrations status
docker exec obs-django python manage.py showmigrations --plan
```

### Method 4: Docker Health Check

```bash
# Check container health status
docker inspect obs-django --format '{{.State.Health.Status}}'

# View health check logs
docker inspect obs-django --format '{{json .State.Health.Log}}' | jq
```

## Logs Location

### Container Logs

```bash
# View container stdout/stderr
docker logs obs-django

# Follow logs in real-time
docker logs -f obs-django

# View last 100 lines
docker logs --tail 100 obs-django
```

### Application Logs

```bash
# View Django application logs
docker exec obs-django cat /app/logs/django.log

# View access logs (Gunicorn)
docker exec obs-django cat /app/logs/access.log

# View error logs
docker exec obs-django cat /app/logs/error.log

# Follow logs in real-time
docker exec -it obs-django tail -f /app/logs/django.log
```

### Log Volume

The logs are stored in a Docker volume mounted at `/app/logs/`:

```bash
# List log files
docker exec obs-django ls -la /app/logs/

# Check log file sizes
docker exec obs-django du -sh /app/logs/*
```

## Configuration Files

### Key Files

| File | Path | Purpose |
|------|------|---------|
| settings.py | `/app/config/settings.py` | Django configuration |
| urls.py | `/app/config/urls.py` | URL routing |
| wsgi.py | `/app/config/wsgi.py` | WSGI application |
| entrypoint.sh | `/app/entrypoint.sh` | Container startup script |
| gunicorn.conf.py | `/app/gunicorn.conf.py` | Gunicorn configuration |

### settings.py Key Configurations

```python
# Prometheus Integration
INSTALLED_APPS = [
    ...
    "django_prometheus",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    ...
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

# Database with Prometheus
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        ...
    }
}

# JSON Logging
LOGGING = {
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            ...
        }
    }
}
```

## Integration Points

### Connected Modules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DJANGO INTEGRATION POINTS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  obs-django                                                                 │
│  ├── ──────────────► obs-postgres (database)                                │
│  │                        Port: 5432                                        │
│  │                        Host: obs-postgres                                │
│  │                                                                          │
│  ├── ──────────────► Prometheus (metrics collection)                        │
│  │                        Endpoint: /metrics                                │
│  │                        Port: 9000                                        │
│  │                                                                          │
│  ├── ──────────────► Promtail (log shipping)                                │
│  │                        Log File: /app/logs/django.log                    │
│  │                                                                          │
│  ├── ◄────────────── obs-nginx (reverse proxy)                              │
│  │                        Port: 80                                          │
│  │                                                                          │
│  └── ◄────────────── Sentry (error tracking)                                │
│                               DSN: via environment variable                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Integration Summary

| Service | Integration Type | Port | Protocol |
|---------|-----------------|------|----------|
| PostgreSQL | Database | 5432 | PostgreSQL |
| Prometheus | Metrics | 9000 | HTTP |
| Promtail | Logs | N/A | File tail |
| Nginx | HTTP Proxy | 80 | HTTP |
| Sentry | Errors | N/A | SDK |

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

**Symptom**: Container exits immediately after starting

**Diagnosis**:
```bash
# Check container logs
docker logs obs-django

# Check if database is ready
docker logs obs-django 2>&1 | grep "database"
```

**Solution**: Ensure PostgreSQL is healthy before Django starts:
```bash
# Check PostgreSQL status
docker ps | grep obs-postgres

# If not healthy, restart PostgreSQL first
docker compose -f django_app/docker-compose.yml restart obs-postgres
```

#### 2. Metrics Not Showing in Prometheus

**Symptom**: Prometheus shows no data for Django

**Diagnosis**:
```bash
# Test metrics endpoint inside container
docker exec obs-django wget -qO- http://127.0.0.1:9000/metrics | head

# Check Prometheus target status
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="django")'
```

**Solution**: Ensure Prometheus is scraping correctly:
- Check prometheus.yml has correct job config
- Verify network connectivity between containers

#### 3. Logs Not Appearing in Loki

**Symptom**: No Django logs in Grafana/Loki

**Diagnosis**:
```bash
# Check if log file exists
docker exec obs-django ls -la /app/logs/

# Check Promtail is tailing the file
docker logs obs-promtail 2>&1 | grep "django.log"

# Query Loki directly
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'
```

**Solution**: Ensure Promtail can access the log volume:
```bash
# Check volume mounts
docker inspect obs-promtail | jq '.[0].Mounts'

# Restart Promtail
docker compose -f django_app/docker-compose.yml restart obs-promtail
```

#### 4. High Memory Usage

**Symptom**: Django container using excessive memory

**Diagnosis**:
```bash
# Check memory usage
docker stats obs-django

# Check Gunicorn workers
docker exec obs-django ps aux | grep gunicorn
```

**Solution**: Adjust Gunicorn worker count in docker-compose.yml:
```yaml
command: gunicorn --workers 2 --bind 0.0.0.0:9000 ...
```

#### 5. Database Connection Errors

**Symptom**: "could not connect to server" errors

**Diagnosis**:
```bash
# Check PostgreSQL is running
docker exec obs-postgres pg_isready

# Test connection from Django
docker exec obs-django python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()"
```

**Solution**: Wait for PostgreSQL to be healthy:
```bash
# Check PostgreSQL health
docker inspect obs-postgres --format '{{.State.Health.Status}}'
```

#### 6. 502 Bad Gateway (Nginx)

**Symptom**: Getting 502 errors when accessing via Nginx

**Diagnosis**:
```bash
# Check if Django is running
docker ps | grep obs-django

# Test Django directly
curl http://localhost:9000/

# Check Nginx logs
docker logs obs-nginx
```

**Solution**: Restart Django and Nginx:
```bash
docker compose -f django_app/docker-compose.yml restart obs-django obs-nginx
```

## Quick Reference

### Docker Commands

```bash
# Start all services
docker compose -f django_app/docker-compose.yml up -d

# Stop all services
docker compose -f django_app/docker-compose.yml down

# Restart Django
docker compose -f django_app/docker-compose.yml restart obs-django

# View logs
docker logs -f obs-django

# Access shell
docker exec -it obs-django /bin/sh
```

> **Note**: These commands assume you are in the project root folder (`django-observability/`).

### URLs

| Service | URL |
|---------|-----|
| Django (direct) | http://localhost:9000 |
| Django (via nginx) | http://localhost |
| Metrics | http://localhost:9000/metrics |
| Admin | http://localhost:9000/admin/ |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DEBUG | Debug mode | True |
| SECRET_KEY | Django secret key | - |
| DB_NAME | Database name | todo_db |
| DB_USER | Database user | postgres |
| DB_PASSWORD | Database password | postgres |
| DB_HOST | Database host | obs-postgres |
| DB_PORT | Database port | 5432 |

### Ports

| Port | Service |
|------|---------|
| 9000 | Django application |
| 80 | Nginx (if running) |
| 5432 | PostgreSQL (internal) |
| 5439 | PostgreSQL (external) |

### Key Metrics

| Metric | Description |
|--------|-------------|
| `django_http_requests_total` | Total HTTP requests by method/status/view |
| `django_http_requests_latency_seconds` | Request duration histogram |
| `django_db_query_duration_seconds` | Database query duration |
| `django_db_errors_total` | Database error count |

### Key Log Labels

| Label | Source | Description |
|-------|--------|-------------|
| `app` | Promtail | Application name (django) |
| `env` | Promtail | Environment (dev) |
| `level` | JSON parsed | Log level (INFO, ERROR, etc.) |
| `logger` | JSON parsed | Logger name |
| `message` | JSON parsed | Log message |

---

## Related Documentation

- [Prometheus](./02-prometheus.md) - Metrics collection
- [Loki](./04-loki.md) - Log aggregation
- [Grafana](./03-grafana.md) - Visualization
- [Promtail](./05-promtail.md) - Log shipping
- [Alertmanager](./06-alertmanager.md) - Alert routing
- [Nginx](./07-nginx.md) - Reverse proxy
