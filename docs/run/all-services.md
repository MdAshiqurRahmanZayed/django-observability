# Run All Services

Complete guide to run and manage all services together.

---

## Quick Start

```bash
# Clone & Navigate
git clone https://github.com/MdAshiqurRahmanZayed/django-observability.git
cd django-observability

# Configure
cp django_app/.env.example django_app/.env

# Start Everything
docker compose -f django_app/docker-compose.yml up -d --build
```

---

## Services Overview

| Service | Port | Purpose | Status Check |
|---------|------|---------|--------------|
| obs-django | 9000 | Django app | `curl http://localhost:9000/metrics` |
| obs-postgres | 5439 | Database | `docker exec obs-postgres pg_isready` |
| obs-prometheus | 9090 | Metrics | `curl http://localhost:9090/-/healthy` |
| obs-grafana | 3000 | Dashboards | `curl http://localhost:3000/api/health` |
| obs-loki | 3100 | Logs | `curl http://localhost:3100/ready` |
| obs-promtail | - | Log shipper | `docker logs obs-promtail` |
| obs-alertmanager | 9093 | Alerts | `curl http://localhost:9093/-/healthy` |
| obs-nginx | 80 | Reverse proxy | `curl http://localhost:80/` |
| obs-node-exporter | 9100 | System metrics | `curl http://localhost:9100/metrics` |
| obs-pgadmin | 5050 | DB admin | `curl http://localhost:5050/` |
| obs-mcp-server | 8000 | AI tools | `curl http://localhost:8000/health` |

---

## Start

### Start All

```bash
docker compose -f django_app/docker-compose.yml up -d
```

### Start with Rebuild

```bash
docker compose -f django_app/docker-compose.yml up -d --build
```

### Start Specific Services

```bash
# Core services
docker compose -f django_app/docker-compose.yml up -d obs-postgres obs-django

# Monitoring stack
docker compose -f django_app/docker-compose.yml up -d obs-prometheus obs-grafana obs-loki obs-promtail

# Alerting
docker compose -f django_app/docker-compose.yml up -d obs-alertmanager

# Infrastructure
docker compose -f django_app/docker-compose.yml up -d obs-nginx obs-node-exporter

# Tools
docker compose -f django_app/docker-compose.yml up -d obs-pgadmin obs-mcp-server
```

---

## Verify All Services

### Quick Check

```bash
docker compose -f django_app/docker-compose.yml ps
```

### Detailed Health Check

```bash
echo "=== Health Check ==="
echo ""

echo "Django:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/metrics
echo "Prometheus:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy
echo "Grafana:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
echo "Loki:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:3100/ready
echo "Alertmanager:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:9093/-/healthy
echo "Nginx:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:80/
echo "MCP Server:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
```

### Expected: All return `200`

---

## Access All Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Django App | http://localhost | - |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |
| Loki API | http://localhost:3100 | - |
| pgAdmin | http://localhost:5050 | admin@admin.com / admin |
| MCP Server | http://localhost:8000 | - |

---

## Stop

### Stop All

```bash
docker compose -f django_app/docker-compose.yml down
```

### Stop with Data Cleanup

```bash
docker compose -f django_app/docker-compose.yml down -v
```

### Stop Specific Services

```bash
docker compose -f django_app/docker-compose.yml stop obs-django obs-prometheus
```

---

## Restart

### Restart All

```bash
docker compose -f django_app/docker-compose.yml restart
```

### Restart Specific Services

```bash
docker compose -f django_app/docker-compose.yml restart obs-django
docker compose -f django_app/docker-compose.yml restart obs-prometheus obs-grafana
```

---

## Logs

### All Services

```bash
docker compose -f django_app/docker-compose.yml logs -f
```

### Specific Service

```bash
docker logs -f obs-django
docker logs -f obs-prometheus
docker logs -f obs-grafana
```

### Last 50 Lines

```bash
docker logs --tail 50 obs-django
```

---

## Resource Usage

```bash
docker stats obs-django obs-prometheus obs-grafana obs-loki obs-postgres
```

---

## Networks

The stack uses two networks:

| Network | Purpose | Services |
|---------|---------|----------|
| app_network | Application | Django, PostgreSQL, Nginx, pgAdmin |
| observability_network | Monitoring | Prometheus, Grafana, Loki, Promtail, Alertmanager, Node Exporter, Django |

Django is on both networks because it needs to:
- Talk to PostgreSQL
- Expose metrics to Prometheus
- Write logs that Promtail reads

---

## Volumes

| Volume | Purpose | Size |
|--------|---------|------|
| postgres_data | PostgreSQL data | ~50MB |
| prometheus_data | Prometheus metrics | ~100MB |
| loki_data | Loki logs | ~200MB |
| grafana_data | Grafana dashboards | ~10MB |
| alertmanager_data | Alertmanager state | ~5MB |
| static_volume | Django static files | ~20MB |
| media_volume | Django media files | - |
| logs_volume | Application logs | ~10MB |
| pgadmin_data | pgAdmin data | ~10MB |

---

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs for errors
docker compose -f django_app/docker-compose.yml logs

# Check if ports are in use
lsof -i :80 :3000 :9000 :9090 :9093 :3100 :5050 :8000
```

### Port Conflicts

```bash
# Find what's using a port
lsof -i :3000

# Kill the process
kill $(lsof -t -i :3000)

# Or change port in docker-compose.yml
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker Desktop memory
# Docker Desktop → Settings → Resources → Memory → 4GB+
```

### Database Connection Issues

```bash
# Check PostgreSQL health
docker inspect obs-postgres --format '{{.State.Health.Status}}'

# Wait for PostgreSQL to be healthy
sleep 10

# Restart Django
docker compose -f django_app/docker-compose.yml restart obs-django
```

### Network Issues

```bash
# List networks
docker network ls

# Inspect network
docker network inspect django_app_observability_network

# Recreate networks
docker compose -f django_app/docker-compose.yml down
docker compose -f django_app/docker-compose.yml up -d
```

---

## Production Considerations

### Environment Variables

Change these in production:

```bash
# Strong passwords
DB_PASSWORD=<strong-password>
GF_ADMIN_PASSWORD=<strong-password>

# Django
DEBUG=False
SECRET_KEY=<random-secret-key>
ALLOWED_HOSTS=your-domain.com

# Slack (real webhook)
SLACK_WEBHOOK_URL=See https://api.slack.com/apps to get your webhook URL
```

### Resource Limits

Add to docker-compose.yml:

```yaml
services:
  obs-django:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### Backups

```bash
# Backup PostgreSQL
docker exec obs-postgres pg_dump -U postgres todo_db > backup.sql

# Backup Prometheus
docker exec obs-prometheus tar -czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp obs-prometheus:/tmp/prometheus-backup.tar.gz ./
```

---

## Quick Reference

```bash
# Start all
docker compose -f django_app/docker-compose.yml up -d

# Stop all
docker compose -f django_app/docker-compose.yml down

# Restart all
docker compose -f django_app/docker-compose.yml restart

# View status
docker compose -f django_app/docker-compose.yml ps

# View logs
docker compose -f django_app/docker-compose.yml logs -f

# Rebuild
docker compose -f django_app/docker-compose.yml up -d --build

# Clean up
docker compose -f django_app/docker-compose.yml down -v
```
