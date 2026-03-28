# Grafana

## Overview

Grafana is the visualization and monitoring UI in this observability stack. It connects to Prometheus and Loki to provide dashboards, graphs, and log exploration for all your metrics and logs.

## Description

Grafana is an open-source visualization and analytics software that allows you to:
- Query and visualize metrics from Prometheus
- Explore and search logs from Loki
- Create and share dashboards
- Set up alerts

In this stack, Grafana:
- Connects to Prometheus for metrics visualization
- Connects to Loki for log exploration
- Provides pre-configured dashboards
- Allows ad-hoc log queries

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       GRAFANA IN STACK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────────┐                               ┌──────────────────┐   │
│   │    Prometheus    │ ◀───────────── GET /metrics   │     Grafana      │   │
│   │      :9090       │                               │      :3000       │   │
│   └──────────────────┘                               └────────┬─────────┘   │
│                                                              │              │
│   ┌──────────────────┐                              ┌────────▼─────────┐    │
│   │      Loki        │ ◀──────── GET /loki/api/v1   │                  │    │
│   │      :3100      │                               │   Dashboards     │    │
│   └──────────────────┘                              │   Graphs         │    │
│                                                     |    Log Explorer  │    │
│                                                     |    Alerts        │    │
│                                                     └-─────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Visualization | Grafana | Latest |
| Metrics | Prometheus | Latest |
| Logs | Loki | 2.9.0 |

## Docker Configuration

### docker-compose.yml

```yaml
obs-grafana:
  image: grafana/grafana:latest
  container_name: obs-grafana
  restart: unless-stopped
  ports:
    - "3000:3000"
  environment:
    GF_SECURITY_ADMIN_USER: ${GF_ADMIN_USER:-admin}
    GF_SECURITY_ADMIN_PASSWORD: ${GF_ADMIN_PASSWORD:-admin}
    GF_PATHS_PROVISIONING: /etc/grafana/provisioning
  volumes:
    - ./../grafana/provisioning:/etc/grafana/provisioning:ro
    - grafana_data:/var/lib/grafana
  depends_on:
    - obs-prometheus
    - obs-loki
  networks:
    - observability_network
```

### datasources.yml (provisioned automatically)

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://obs-prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://obs-loki:3100
```

## Network Access

| Access | URL |
|--------|-----|
| External (host) | http://localhost:3000 |
| Internal (Docker) | http://obs-grafana:3000 |

**Default Credentials:** admin / admin

## Data Sources

Grafana is pre-configured with these datasources:

| Datasource | URL | Purpose |
|------------|-----|---------|
| Prometheus | http://obs-prometheus:9090 | Metrics |
| Loki | http://obs-loki:3100 | Logs |

## Grafana Features

### Explore

Use Grafana Explore to:
- Query metrics with PromQL
- Search logs with LogQL
- View log entries with details

### Dashboards

Pre-built dashboards for:
- Django request metrics
- Database performance
- System resources (CPU, Memory, Disk)
- Custom application metrics

### Alerting

Set up alerts based on:
- Metric thresholds
- Log patterns

## Useful Commands

### Container Management

```bash
# Restart Grafana
docker compose -f django_app/docker-compose.yml restart obs-grafana

# View logs
docker logs -f obs-grafana

# Access shell
docker exec -it obs-grafana /bin/sh
```

### Access Grafana API

```bash
# Get datasources
curl -u admin:admin http://localhost:3000/api/datasources

# Get dashboards
curl -u admin:admin http://localhost:3000/api/search

# Query Prometheus from Grafana
curl -u admin:admin 'http://localhost:3000/api/datasources/uid/prometheus/api/v1/query?query=up'
```

### Reset Password

```bash
# Reset admin password via environment
# Edit docker-compose.yml:
#   GF_SECURITY_ADMIN_PASSWORD: newpassword

# Restart and login with admin/newpassword
docker compose -f django_app/docker-compose.yml restart obs-grafana
```

## Expected Output

### Login Page

```
URL: http://localhost:3000
Username: admin
Password: admin
```

### Explore - Metrics

```
1. Click "Explore" (sidebar)
2. Select "Prometheus" from dropdown
3. Enter PromQL query: up
4. Click "Run Query"
5. See results in graph + table
```

### Explore - Logs

```
1. Click "Explore" (sidebar)
2. Select "Loki" from dropdown
3. Enter LogQL: {app="django"}
4. Click "Run Query"
5. See log entries with expandable details
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/datasources` | GET | List datasources |
| `/api/dashboards` | GET | List dashboards |
| `/api/search` | GET | Search dashboards |
| `/api/health` | GET | Health check |

## Health Checks

```bash
# Health check
curl -f http://localhost:3000/api/health || echo "Grafana is down"

# Check datasources
curl -u admin:admin http://localhost:3000/api/datasources | jq

# Check version
curl http://localhost:3000/api/health
```

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| datasources.yml | grafana/provisioning/datasources/datasources.yml | Datasource config |
| dashboard.yml | grafana/provisioning/dashboards/dashboard.yml | Dashboard config |

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Prometheus | Query :9090 | Metrics source |
| Loki | Query :3100 | Log source |

## Troubleshooting

### Cannot Connect to Prometheus

```bash
# Check datasource config
curl -u admin:admin http://localhost:3000/api/datasources | jq

# Test Prometheus directly
curl http://localhost:9090/-/healthy

# Check network
docker network inspect django_app_observability_network | grep grafana
```

### Cannot Connect to Loki

```bash
# Check datasource
curl -u admin:admin http://localhost:3000/api/datasources/uid/loki

# Test Loki directly
curl http://localhost:3100/ready

# Check Loki logs
docker logs obs-loki
```

### Login Issues

```bash
# Reset password
docker compose -f django_app/docker-compose.yml stop obs-grafana

# Edit .env with new password
# GF_ADMIN_PASSWORD=yournewpassword

# Restart
docker compose -f django_app/docker-compose.yml up -d obs-grafana
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-grafana

# Stop
docker compose -f django_app/docker-compose.yml stop obs-grafana

# Restart
docker compose -f django_app/docker-compose.yml restart obs-grafana

# View logs
docker logs -f obs-grafana
```

### URLs

| Service | URL |
|---------|-----|
| Grafana UI | http://localhost:3000 |
| Explore | http://localhost:3000/explore |
| Dashboards | http://localhost:3000/dashboards |
| Alerting | http://localhost:3000/alerting |

### Key Ports

| Port | Service |
|------|---------|
| 3000 | Grafana UI |

### Default Credentials

| Field | Value |
|-------|-------|
| Username | admin |
| Password | admin |

### Useful Queries

**PromQL (Metrics):**
| Query | Description |
|-------|-------------|
| `up` | Target status |
| `rate(django_http_requests_total[5m])` | Request rate |
| `histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m]))` | P95 latency |

**LogQL (Logs):**
| Query | Description |
|-------|-------------|
| `{app="django"}` | All Django logs |
| `{app="django", level="ERROR"}` | Django errors |
| `{app="django"} \|= "POST"` | Logs containing "POST" |

---

## Related Documentation

- [Prometheus](./02-prometheus.md) - Metrics source
- [Loki](./04-loki.md) - Log source
- [Alertmanager](./06-alertmanager.md) - Alert routing
