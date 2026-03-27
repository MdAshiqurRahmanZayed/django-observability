# Observability Stack Documentation

This directory contains comprehensive documentation for each component in the Django Observability Stack.

## Overview

The observability stack provides complete monitoring for your Django application:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY STACK ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│   │   Nginx     │───▶│   Django    │───▶│PostgreSQL   │    │  Sentry     │ │
│   │   :80       │    │   :9000     │    │   :5432     │    │  (errors)   │ │
│   └─────────────┘    └──────┬──────┘    └─────────────┘    └─────────────┘ │
│                            │                                             │
│         ┌──────────────────┼──────────────────┐                            │
│         │                  │                  │                            │
│         ▼                  ▼                  ▼                            │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│   │ Prometheus  │    │   Promtail  │    │  Sentry SDK │                     │
│   │ (metrics)  │    │   (logs)    │    │  (errors)   │                     │
│   └──────┬──────┘    └──────┬──────┘    └─────────────┘                     │
│          │                 │                                               │
│          ▼                 ▼                                               │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                      │
│   │Alertmanager│    │    Loki     │    │   Grafana   │                      │
│   │ (alerts)   │    │  (storage)  │    │   (UI)      │                      │
│   └─────────────┘    └─────────────┘    └─────────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Documentation Modules

| # | Module | Description |
|---|--------|-------------|
| 01 | [Django App](./01-django-app.md) | Application with metrics & logging |
| 02 | [Prometheus](./02-prometheus.md) | Metrics collection & alerting |
| 03 | [Grafana](./03-grafana.md) | Visualization & dashboards |
| 04 | [Loki](./04-loki.md) | Log aggregation |
| 05 | [Promtail](./05-promtail.md) | Log shipping agent |
| 06 | [Alertmanager](./06-alertmanager.md) | Alert routing & notifications |
| 07 | [Nginx](./07-nginx.md) | Reverse proxy & static files |
| 08 | [MCP Server](./08-mcp-server.md) | AI tool integration |
| 09 | [PostgreSQL](./09-postgres.md) | Database & data persistence |

## Quick Start

### Start All Services

```bash
cd django-observability
docker compose -f django_app/docker-compose.yml up -d
```

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Django | http://localhost | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |
| Loki | http://localhost:3100 | - |
| pgAdmin | http://localhost:5050 | admin@admin.com/admin |

### Key Commands

```bash
# Start all services
docker compose -f django_app/docker-compose.yml up -d

# Stop all services
docker compose -f django_app/docker-compose.yml down

# View logs
docker logs -f <container-name>

# Restart specific service
docker compose -f django_app/docker-compose.yml restart obs-django

# Access container shell
docker exec -it <container-name> /bin/sh
```

## Data Flow Summary

### Metrics Flow (Pull Model)

```
Django → /metrics → Prometheus (scrape) → Alertmanager (alerts) → Slack
                                    ↓
                               Grafana (graphs)
```

### Logs Flow (Push Model)

```
Django → /app/logs/django.log → Promtail (tail) → Loki (store) → Grafana (query)
```

### Alert Flow

```
Prometheus (rules) → Alertmanager (grouping) → Slack channels
```

## Common Queries

### Prometheus (PromQL)

```promql
up                          -- Target status
rate(http_requests_total[5m])  -- Request rate
histogram_quantile(0.95, rate(latency_bucket[5m])) -- P95 latency
```

### Loki (LogQL)

```logql
{app="django"}                    -- All Django logs
{app="django", level="ERROR"}      -- Django errors
{app="django"} |= "POST"           -- Contains "POST"
```

## Project Structure

```
django-observability/
├── django_app/
│   ├── docker-compose.yml    # All services config
│   └── ...
├── docs/                    # This documentation
│   ├── 01-django-app.md
│   ├── 02-prometheus.md
│   ├── 03-grafana.md
│   ├── 04-loki.md
│   ├── 05-promtail.md
│   ├── 06-alertmanager.md
│   ├── 07-nginx.md
│   ├── 08-mcp-server.md
│   └── 09-postgres.md
├── prometheus/
│   ├── prometheus.yml        # Scrape config
│   └── rules/                # Alert rules
├── loki/
│   └── loki-config.yml
├── promtail/
│   └── promtail-config.yml
├── alertmanager/
│   └── alertmanager.yml
├── grafana/
│   └── provisioning/         # Datasources & dashboards
└── nginx/
    └── nginx.conf
```

## Environment Variables

Create `django_app/.env` from `.env.example`:

```bash
# Database
DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=obs-postgres
DB_PORT=5432

# Grafana
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin

# Slack (for alerts)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## Troubleshooting

### Services Not Starting

```bash
# Check Docker is running
docker ps

# Check logs
docker compose -f django_app/docker-compose.yml logs

# Rebuild containers
docker compose -f django_app/docker-compose.yml up -d --build
```

### Network Issues

```bash
# Check networks
docker network ls

# Inspect specific network
docker network inspect django_app_observability_network
```

### Port Conflicts

If ports are already in use:

```bash
# Find what's using the port
lsof -i :3000

# Stop the conflicting service or change port in docker-compose.yml
```

## License

This is an educational project for demonstrating observability best practices with Django.
