# Configuration

## Environment Variables

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_NAME` | todo_db | Database name |
| `DB_USER` | postgres | Database username |
| `DB_PASSWORD` | postgres | Database password |
| `DB_HOST` | obs-postgres | Database host |
| `DB_PORT` | 5432 | Database port |

### Django

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | True | Debug mode |
| `SECRET_KEY` | - | Django secret key |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Allowed hosts |

### Grafana

| Variable | Default | Description |
|----------|---------|-------------|
| `GF_ADMIN_USER` | admin | Admin username |
| `GF_ADMIN_PASSWORD` | admin | Admin password |

### Sentry

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | - | Sentry DSN |
| `DJANGO_ENV` | development | Environment |

### Slack

| Variable | Default | Description |
|----------|---------|-------------|
| `SLACK_WEBHOOK_URL` | - | Slack webhook URL |

---

## Docker Compose

### Service Configuration

```yaml
obs-django:
  image: django-observability:latest
  container_name: obs-django
  restart: on-failure
  ports:
    - "9000:9000"
  volumes:
    - static_volume:/app/staticfiles
    - media_volume:/app/mediafiles
    - logs_volume:/app/logs
  env_file:
    - .env
  depends_on:
    obs-postgres:
      condition: service_healthy
  networks:
    - app_network
    - observability_network
```

---

## Prometheus

### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["obs-alertmanager:9093"]

rule_files:
  - /etc/prometheus/rules/*.yml

scrape_configs:
  - job_name: "django"
    static_configs:
      - targets: ["obs-django:9000"]
    metrics_path: /metrics
```

### Storage Options

| Option | Default | Description |
|--------|---------|-------------|
| `storage.tsdb.path` | /prometheus | Data directory |
| `storage.tsdb.retention.time` | 15d | Data retention |

---

## Loki

### loki-config.yml

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1

limits_config:
  retention_period: 30d
  ingestion_rate_mb: 16
```

### Storage Options

| Option | Default | Description |
|--------|---------|-------------|
| `retention_period` | 30d | Log retention |
| `ingestion_rate_mb` | 16 | Max ingestion rate |
| `schema` | v12 | Index schema |

---

## Alertmanager

### alertmanager.yml

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: "SLACK_WEBHOOK_URL_PLACEHOLDER"

route:
  group_by: ["alertname", "category"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: "slack-default"
```

### Routing Options

| Option | Default | Description |
|--------|---------|-------------|
| `group_by` | alertname, category | Group alerts |
| `group_wait` | 30s | Wait before sending |
| `group_interval` | 5m | Between groups |
| `repeat_interval` | 12h | Repeat alerts |

---

## Nginx

### nginx.conf

```nginx
upstream django {
    server obs-django:9000;
}

server {
    listen 80;
    server_name localhost;

    location /static/ {
        alias /app/static/;
    }

    location /media/ {
        alias /app/mediafiles/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Django Settings

### Key Configuration

```python
INSTALLED_APPS = [
    "django_prometheus",
    "todo",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    # ... other middleware ...
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        # ... credentials ...
    }
}

LOGGING = {
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        },
    },
}
```
