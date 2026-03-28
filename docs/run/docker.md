# Docker Commands

All Docker commands for managing the observability stack.

!!! note "Project Root"
    All commands assume you are in the project root: `django-observability/`

---

## Start Services

### Start All

```bash
docker compose -f django_app/docker-compose.yml up -d
```

### Start Specific Service

```bash
docker compose -f django_app/docker-compose.yml up -d obs-django
docker compose -f django_app/docker-compose.yml up -d obs-prometheus
docker compose -f django_app/docker-compose.yml up -d obs-grafana
docker compose -f django_app/docker-compose.yml up -d obs-loki
docker compose -f django_app/docker-compose.yml up -d obs-alertmanager
docker compose -f django_app/docker-compose.yml up -d obs-pgadmin
```

### Rebuild & Start

```bash
# Rebuild Django only
docker compose -f django_app/docker-compose.yml up -d --build obs-django

# Rebuild all
docker compose -f django_app/docker-compose.yml up -d --build
```

---

## Stop Services

### Stop All

```bash
docker compose -f django_app/docker-compose.yml down
```

### Stop Specific Service

```bash
docker compose -f django_app/docker-compose.yml stop obs-django
docker compose -f django_app/docker-compose.yml stop obs-prometheus
docker compose -f django_app/docker-compose.yml stop obs-grafana
```

---

## Restart Services

### Restart All

```bash
docker compose -f django_app/docker-compose.yml restart
```

### Restart Specific Service

```bash
docker compose -f django_app/docker-compose.yml restart obs-django
docker compose -f django_app/docker-compose.yml restart obs-prometheus
docker compose -f django_app/docker-compose.yml restart obs-grafana
docker compose -f django_app/docker-compose.yml restart obs-loki
docker compose -f django_app/docker-compose.yml restart obs-alertmanager
docker compose -f django_app/docker-compose.yml restart obs-pgadmin
```

---

## View Status

### List Running Services

```bash
docker compose -f django_app/docker-compose.yml ps
```

### List All (including stopped)

```bash
docker compose -f django_app/docker-compose.yml ps -a
```

---

## View Logs

### All Services

```bash
docker compose -f django_app/docker-compose.yml logs -f
```

### Specific Service

```bash
docker logs -f obs-django
docker logs -f obs-prometheus
docker logs -f obs-grafana
docker logs -f obs-loki
docker logs -f obs-alertmanager
docker logs -f obs-pgadmin
docker logs -f obs-promtail
docker logs -f obs-nginx
docker logs -f obs-node-exporter
```

### Last N Lines

```bash
docker logs --tail 100 obs-django
docker logs --tail 50 obs-prometheus
```

---

## Shell Access

### Access Container Shell

```bash
# Django (Alpine - use /bin/sh)
docker exec -it obs-django /bin/sh

# Prometheus
docker exec -it obs-prometheus /bin/sh

# Grafana
docker exec -it obs-grafana /bin/sh

# Loki
docker exec -it obs-loki /bin/sh

# PostgreSQL
docker exec -it obs-postgres psql -U postgres -d todo_db

# Nginx
docker exec -it obs-nginx /bin/sh
```

---

## Resource Usage

### Container Stats

```bash
docker stats obs-django obs-prometheus obs-grafana obs-loki
```

### Disk Usage

```bash
docker system df
docker volume ls
```

---

## Cleanup

### Remove Stopped Containers

```bash
docker compose -f django_app/docker-compose.yml rm
```

### Remove Volumes (Data Loss!)

```bash
docker compose -f django_app/docker-compose.yml down -v
```

### Remove Everything

```bash
docker compose -f django_app/docker-compose.yml down -v --rmi all
docker system prune -a
```

---

## Health Checks

### Quick Check

```bash
# Django
curl -f http://localhost:9000/metrics | head -1

# Prometheus
curl -f http://localhost:9090/-/healthy

# Grafana
curl -f http://localhost:3000/api/health

# Loki
curl -f http://localhost:3100/ready

# Alertmanager
curl -f http://localhost:9093/-/healthy

# Nginx
curl -f http://localhost:80/
```

### Check All

```bash
echo "Django:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/metrics
echo "Prometheus:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy
echo "Grafana:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
echo "Loki:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:3100/ready
echo "Alertmanager:" && curl -s -o /dev/null -w "%{http_code}" http://localhost:9093/-/healthy
```

---

## Networks

### List Networks

```bash
docker network ls
```

### Inspect Network

```bash
docker network inspect django_app_observability_network
docker network inspect django_app_app_network
```

### Connect Container to Network

```bash
docker network connect django_app_observability_network obs-pgadmin
```

---

## Volumes

### List Volumes

```bash
docker volume ls | grep django_app
```

### Inspect Volume

```bash
docker volume inspect django_app_prometheus_data
docker volume inspect django_app_loki_data
docker volume inspect django_app_grafana_data
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs obs-django

# Check if port is in use
lsof -i :9000

# Check disk space
df -h
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase Docker Desktop memory
# Docker Desktop → Settings → Resources → Memory
```

### Network Issues

```bash
# Check container IP
docker inspect obs-django | grep IPAddress

# Test connectivity
docker exec obs-django ping obs-postgres
docker exec obs-prometheus wget -qO- http://obs-django:9000/metrics
```
