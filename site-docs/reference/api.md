# API Endpoints

## Overview

This page lists all API endpoints available in the observability stack.

---

## Django Application

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page |
| `/admin/` | GET | Django admin panel |
| `/todo/` | GET/POST | Todo list |
| `/todo/<id>/` | GET/PUT/DELETE | Todo management |
| `/metrics` | GET | Prometheus metrics |
| `/accounts/login/` | GET/POST | User login |

---

## Prometheus

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metrics` | GET | All metrics |
| `/api/v1/query` | GET | PromQL instant query |
| `/api/v1/query_range` | GET | PromQL range query |
| `/api/v1/targets` | GET | Scrape targets |
| `/api/v1/rules` | GET | Alert rules |
| `/api/v1/alerts` | GET | Alert states |
| `/api/v1/alertmanagers` | GET | Alertmanager config |
| `/-/healthy` | GET | Health check |

### Example Queries

```bash
# Query all targets
curl http://localhost:9090/api/v1/targets | jq

# Query Django request rate
curl 'http://localhost:9090/api/v1/query?query=rate(django_http_requests_total[5m])'

# Query range (last hour)
curl 'http://localhost:9090/api/v1/query_range?query=up&start=1773532800&end=1773536400&step=60s'
```

---

## Loki

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/loki/api/v1/push` | POST | Push log entries |
| `/loki/api/v1/query` | GET | Instant query |
| `/loki/api/v1/query_range` | GET | Range query |
| `/loki/api/v1/label` | GET | List labels |
| `/loki/api/v1/label/{name}/values` | GET | Label values |
| `/ready` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |

### Example Queries

```bash
# Push logs
curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test"},"values":[["'"$(date +%s)"'000000000","test"]]}]}'

# Query logs
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'

# Query range
curl 'http://localhost:3100/loki/api/v1/query_range?query=%7Bapp%3D%22django%22%7D&start=1773532800000000000&end=1773536400000000000&limit=100'
```

---

## Grafana

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/datasources` | GET | List datasources |
| `/api/dashboards` | GET | List dashboards |
| `/api/search` | GET | Search |
| `/api/alerts` | GET | List alerts |

### Example Queries

```bash
# Health check
curl http://localhost:3000/api/health

# List datasources
curl -u admin:admin http://localhost:3000/api/datasources | jq

# Search dashboards
curl -u admin:admin http://localhost:3000/api/search | jq
```

---

## Alertmanager

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/alerts` | POST | Receive alerts |
| `/api/v1/alerts` | GET | List active alerts |
| `/api/v1/status` | GET | Status |
| `/healthy` | GET | Health check |

### Example Queries

```bash
# Check status
curl http://localhost:9093/api/v1/status | jq

# List alerts
curl http://localhost:9093/api/v1/alerts | jq
```

---

## Node Exporter

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metrics` | GET | System metrics |

### Example Queries

```bash
# Get all metrics
curl http://localhost:9100/metrics

# Get CPU metrics
curl http://localhost:9100/metrics | grep node_cpu

# Get memory metrics
curl http://localhost:9100/metrics | grep node_memory
```

---

## MCP Server

| Tool | Description |
|------|-------------|
| `check_service_health` | Check all services |
| `get_server_resources` | CPU, memory, disk usage |
| `get_django_metrics` | Django HTTP metrics |
| `get_todo_stats` | Todo statistics |
| `list_todos` | List todos |
| `create_todo` | Create todo |
| `update_todo` | Update todo |
| `delete_todo` | Delete todo |
| `get_grafana_dashboards` | List dashboards |
| `get_grafana_alerts` | List alerts |
| `prometheus_query` | Run PromQL query |
