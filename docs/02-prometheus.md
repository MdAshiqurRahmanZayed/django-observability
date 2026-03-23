# Prometheus

## Overview

Prometheus is the metrics collection and time-series database in this observability stack. It pulls metrics from configured targets, stores them with timestamps and labels, and evaluates alert rules to trigger notifications.

## Description

Prometheus is an open-source monitoring system with a dimensional data model, flexible query language, efficient time series database and modern alerting approach. In this stack, it:

- Scrapes metrics from Django, Node Exporter, Loki, and Grafana
- Stores time-series data in its built-in TSDB (Time Series Database)
- Evaluates alert rules every 15 seconds
- Sends firing alerts to Alertmanager

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMETHEUS IN STACK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   SCRAPING (Pull Model)                                                     │
│   ─────────────────────                                                     │
│                                                                             │
│   ┌─────────────┐     GET /metrics      ┌─────────────────────┐             │
│   │   Django    │ ◀───────────────────▶ │     Prometheus      │             │
│   │   :9000     │                       │       :9090         │             │
│   └─────────────┘                       └──────────┬──────────┘             │
│                                                    │                        │
│   ┌─────────────┐     GET /metrics                 │                        │
│   │ Node Exp    │ ◀────────────────────────────-───┤                        │
│   │   :9100     │                                  │                        │
│   └─────────────┘                                  │                        │
│                                                    │                        │
│   ALERTS                                           |                        │
│   ──────                                           |                        │
│                                                    │                        │
│                                                    ▼                        │
│                                          ┌─────────────────────┐            │
│                                          │   Alertmanager      │            │
│                                          │       :9093         │            │
│                                          └─────────────────────┘            │
│                                                                             │
│   QUERIES (via Grafana)                                                     │
│   ───────────────────                                                       │
│                                                   │                         │
│                                          ┌────────▼──────────┐              │
│                                          │     Grafana       │              │
│                                          │       :3000       │              │
│                                          └───────────────────┘              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Monitoring | Prometheus | Latest |
| Storage | TSDB (built-in) | - |
| Alerting | Alertmanager | Latest |

## Docker Configuration

### docker-compose.yml

```yaml
obs-prometheus:
  image: prom/prometheus:latest
  container_name: obs-prometheus
  restart: unless-stopped
  ports:
    - "9090:9090"
  volumes:
    - ./../prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ./../prometheus/rules:/etc/prometheus/rules:ro
    - prometheus_data:/prometheus
  command:
    - "--config.file=/etc/prometheus/prometheus.yml"
    - "--storage.tsdb.path=/prometheus"
    - "--storage.tsdb.retention.time=15d"
    - "--web.enable-lifecycle"
  networks:
    - observability_network
```

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
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "django"
    static_configs:
      - targets: ["obs-django:9000"]
    metrics_path: /metrics

  - job_name: "node"
    static_configs:
      - targets: ["obs-node-exporter:9100"]

  - job_name: "loki"
    static_configs:
      - targets: ["obs-loki:3100"]
    metrics_path: /metrics

  - job_name: "grafana"
    static_configs:
      - targets: ["obs-grafana:3000"]
    metrics_path: /metrics
```

## Network Access

| Access | URL |
|--------|-----|
| External (host) | http://localhost:9090 |
| Internal (Docker) | http://obs-prometheus:9090 |

## Data Flow

### Scrape Flow

```
1. Prometheus waits for scrape_interval (15s)
        │
        ▼
2. For each target in scrape_configs:
   - Connect to target:port
   - GET /metrics_path
        │
        ▼
3. Parse response as Prometheus exposition format
   Extract: metric_name{labels} value timestamp
        │
        ▼
4. Store in TSDB (Time Series Database)
   File: /prometheus/chunks/
        │
        ▼
5. Next scrape cycle repeats
```

### Alert Flow

```
1. Prometheus evaluates rules every evaluation_interval (15s)
        │
        ▼
2. For each rule:
   - Run PromQL expression
   - Check if threshold exceeded for "for" duration
        │
        ▼
3. If alert fires:
   - Send to Alertmanager POST /api/v1/alerts
        │
        ▼
4. Alertmanager:
   - Groups alerts
   - Routes to Slack channels
   - Sends notifications
```

## Scrape Targets

| Job | Target | Endpoint | Purpose |
|-----|--------|----------|---------|
| prometheus | localhost:9090 | /metrics | Monitor itself |
| django | obs-django:9000 | /metrics | Application metrics |
| node | obs-node-exporter:9100 | /metrics | System metrics |
| loki | obs-loki:3100 | /metrics | Loki metrics |
| grafana | obs-grafana:3000 | /metrics | Grafana metrics |

## Alert Rules

Alert rules are defined in `prometheus/rules/alerts.yml`:

### Alert Categories

| Category | Alerts |
|----------|--------|
| **Database** | DBHighErrorRate, DBSlowQueries, DBHighQueryRate |
| **HTTP** | DjangoDown, Django5xxError, Django4xxError, HighHTTP5xxRate, HighHTTP4xxRate |
| **Latency** | HighP95Latency, HighP99Latency, EndpointSlowResponse |
| **Infrastructure** | HighCPUUsage, CriticalCPUUsage, HighMemoryUsage, CriticalMemoryUsage, HighDiskUsage, DjangoHighMemory |

## Useful Commands

### Container Management

```bash
# Restart Prometheus
docker compose -f django_app/docker-compose.yml restart obs-prometheus

# View logs
docker logs -f obs-prometheus

# Access shell
docker exec -it obs-prometheus /bin/sh
```

### Query Metrics

```bash
# Query all targets
curl http://localhost:9090/api/v1/targets | jq

# Query up metric (is target up?)
curl 'http://localhost:9090/api/v1/query?query=up'

# Query Django request rate
curl 'http://localhost:9090/api/v1/query?query=rate(django_http_requests_total[5m])'

# Query all Django metrics
curl http://localhost:9090/metrics | grep "^django_"
```

### Alert Management

```bash
# View all alert rules
curl http://localhost:9090/api/v1/rules | jq

# View firing alerts
curl http://localhost:9090/api/v1/alerts | jq

# Pause/Resume alerts (requires config reload)
docker exec obs-prometheus kill -HUP 1
```

### Storage Inspection

```bash
# Check TSDB storage size
docker exec obs-prometheus du -sh /prometheus

# List TSDB chunks
docker exec obs-prometheus ls -la /prometheus/chunks/
```

## Expected Output

### Targets Status

```bash
$ curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health, lastError: .lastError}'

{
  "job": "django",
  "health": "up",
  "lastError": ""
}
{
  "job": "node",
  "health": "up",
  "lastError": ""
}
{
  "job": "loki",
  "health": "up",
  "lastError": ""
}
```

### Sample Metrics

```bash
$ curl http://localhost:9090/metrics | grep -E "^django_|^up"

# HELP django_http_requests_total Total number of HTTP requests
# TYPE django_http_requests_total counter
django_http_requests_total{method="GET",status="200",view="todo_list"} 1234

# HELP up Was the target scrape successful
# TYPE up gauge
up{job="django",endpoint="metrics"} 1

# HELP node_cpu_seconds_total Seconds the CPUs spent in each mode
# TYPE node_cpu_seconds_total counter
node_cpu_seconds_total{mode="idle",cpu="0"} 1234567.89
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metrics` | GET | All metrics in Prometheus format |
| `/api/v1/query` | GET | PromQL instant query |
| `/api/v1/query_range` | GET | PromQL range query |
| `/api/v1/targets` | GET | Scrape targets status |
| `/api/v1/rules` | GET | Loaded rules |
| `/api/v1/alerts` | GET | Alert states |
| `/api/v1/alertmanagers` | GET | Alertmanager config |

### Query Examples

```bash
# Instant query
curl 'http://localhost:9090/api/v1/query?query=up'

# Range query (last 1 hour, 1min step)
curl 'http://localhost:9090/api/v1/query_range?query=up&start=1773532800&end=1773536400&step=60s'
```

## Health Checks

```bash
# Check if Prometheus is responding
curl -f http://localhost:9090/-/healthy || echo "Prometheus is down"

# Check targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health=="down")'

# Check Prometheus version
curl http://localhost:9090/api/v1/status/config | jq '.data.yaml'
```

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| prometheus.yml | prometheus/prometheus.yml | Scrape configuration |
| alerts.yml | prometheus/rules/alerts.yml | Alert rules |

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Django | Scrape :9000/metrics | App metrics |
| Node Exporter | Scrape :9100/metrics | System metrics |
| Loki | Scrape :3100/metrics | Loki metrics |
| Grafana | Scrape :3000/metrics | Grafana metrics |
| Alertmanager | Send alerts :9093 | Alert routing |

## Troubleshooting

### Target Down

```bash
# Check target status
curl http://localhost:9090/api/v1/targets | jq

# Test connectivity from Prometheus
docker exec obs-prometheus wget -qO- http://obs-django:9000/metrics

# Check network
docker network inspect django_app_observability_network
```

### Alerts Not Firing

```bash
# Check rule evaluation
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.type=="alerting")'

# Check alert states
curl http://localhost:9090/api/v1/alerts | jq

# Test alert rule manually
curl 'http://localhost:9090/api/v1/query?query=up{job="django"}==0'
```

### High Storage Usage

```bash
# Check storage
docker exec obs-prometheus du -sh /prometheus

# Check retention
docker exec obs-prometheus ls -la /prometheus/ | grep -E "chunks|wal"

# Manual cleanup (be careful!)
docker exec obs-prometheus rm -rf /prometheus/wal/*
docker exec obs-prometheus kill -HUP 1
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-prometheus

# Stop
docker compose -f django_app/docker-compose.yml stop obs-prometheus

# Restart
docker compose -f django_app/docker-compose.yml restart obs-prometheus

# View logs
docker logs -f obs-prometheus

# Access shell
docker exec -it obs-prometheus /bin/sh
```

### URLs

| Service | URL |
|---------|-----|
| Prometheus UI | http://localhost:9090 |
| Metrics | http://localhost:9090/metrics |
| Targets | http://localhost:9090/targets |
| Graph | http://localhost:9090/graph |
| Alerts | http://localhost:9090/alerts |

### Key Ports

| Port | Service |
|------|---------|
| 9090 | Prometheus UI/API |

### Key Metrics

| Metric | Description |
|--------|-------------|
| `up` | Target availability (1=up, 0=down) |
| `scrape_duration_seconds` | Scrape duration |
| `scrape_samples_scraped` | Samples collected |
| `prometheus_target_scrape_pool_exceeded_target_limit` | Target limit exceeded |

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| scrape_interval | 15s | How often to scrape targets |
| evaluation_interval | 15s | How often to evaluate rules |
| storage.tsdb.retention.time | 15d | How long to keep data |
| storage.tsdb.path | /prometheus | Data directory |

---

## Related Documentation

- [Django App](./01-django-app.md) - Metrics source
- [Alertmanager](./06-alertmanager.md) - Alert routing
- [Grafana](./03-grafana.md) - Visualization
- [Loki](./04-loki.md) - Log aggregation
