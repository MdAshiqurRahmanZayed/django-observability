# Troubleshooting

## Common Issues

### Services Not Starting

**Symptom**: Container exits immediately

**Solution**:
```bash
# Check logs
docker compose -f django_app/docker-compose.yml logs

# Check if all services are healthy
docker ps

# Restart services
docker compose -f django_app/docker-compose.yml up -d
```

---

### Database Connection Failed

**Symptom**: "could not connect to server" errors

**Diagnosis**:
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection from Django
docker exec obs-django python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()"
```

**Solution**: Wait for PostgreSQL health check:
```bash
# Check PostgreSQL health
docker inspect obs-postgres --format '{{.State.Health.Status}}'
```

---

### Prometheus Target Down

**Symptom**: Target shows as "down" in Prometheus UI

**Diagnosis**:
```bash
# Check target status
curl http://localhost:9090/api/v1/targets | jq

# Test connectivity from Prometheus
docker exec obs-prometheus wget -qO- http://obs-django:9000/metrics
```

**Solution**: Ensure services are on same network:
```bash
# Check network connectivity
docker network inspect django_app_observability_network
```

---

### Logs Not Appearing in Loki

**Symptom**: No Django logs in Grafana

**Diagnosis**:
```bash
# Check if log file exists
docker exec obs-django ls -la /app/logs/

# Check Promtail is tailing
docker logs obs-promtail | grep "django.log"

# Query Loki
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'
```

**Solution**: Restart Promtail:
```bash
docker compose -f django_app/docker-compose.yml restart obs-promtail
```

---

### 502 Bad Gateway

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

---

### Alerts Not Firing

**Symptom**: No alerts in Slack

**Diagnosis**:
```bash
# Check Prometheus rules
curl http://localhost:9090/api/v1/rules | jq

# Check Alertmanager status
curl http://localhost:9093/api/v1/status | jq

# Test webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' $SLACK_WEBHOOK_URL
```

**Solution**: Ensure webhook URL is set:
```bash
grep SLACK_WEBHOOK_URL django_app/.env
```

---

### High Memory Usage

**Symptom**: Container using excessive memory

**Diagnosis**:
```bash
# Check memory usage
docker stats

# Check Gunicorn workers
docker exec obs-django ps aux | grep gunicorn
```

**Solution**: Adjust worker count:
```yaml
command: gunicorn --workers 2 --bind 0.0.0.0:9000 ...
```

---

## Quick Reference

### Restart All Services

```bash
docker compose -f django_app/docker-compose.yml down
docker compose -f django_app/docker-compose.yml up -d
```

### View All Logs

```bash
docker compose -f django_app/docker-compose.yml logs -f
```

### Check Service Health

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health

# Loki
curl http://localhost:3100/ready

# Alertmanager
curl http://localhost:9093/healthy
```

### Clear All Data

```bash
docker compose -f django_app/docker-compose.yml down -v
docker compose -f django_app/docker-compose.yml up -d
```

---

## Get Help

- GitHub Issues: [github.com/MdAshiqurRahmanZayed/django-observability/issues](https://github.com/MdAshiqurRahmanZayed/django-observability/issues)
- Discord: [opencode.ai/discord](https://opencode.ai/discord)
