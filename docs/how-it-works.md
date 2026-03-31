# How It Works: Complete Guide

This guide explains every tool in the observability stack, how they work, how they're configured, and how they connect to each other.

---

## Overview

The observability stack consists of 6 main tools:

| Tool | Role | Purpose |
|------|------|---------|
| [Prometheus](#prometheus) | Metrics collection | Collects and stores metrics from applications |
| [Loki](#loki) | Log storage | Stores and indexes log data |
| [Promtail](#promtail) | Log shipping | Reads log files and sends to Loki |
| [Alertmanager](#alertmanager) | Alert routing | Routes alerts to Slack channels |
| [Grafana](#grafana) | Visualization | Displays dashboards from Prometheus and Loki |
| [Node Exporter](#node-exporter) | Host metrics | Collects CPU, memory, disk metrics |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY STACK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌──────────────┐                    ┌───────────────────────┐            │
│    │   Browser    │                    │      Django App       │            │
│    │              │──── HTTP ────────▶│     obs-django:9000    │            │
│    └──────────────┘                    │                       │            │
│                                        │  - Serves pages       │            │
│                                        │  - Writes logs        │            │
│                                        │  - Exposes /metrics   │            │
│                                        └───────────┬───────────┘            │
│                                                    │                        │
│                              ┌─────────────────────┼─────────────────────┐  │
│                              │                     │                     │  │
│                              ▼                     ▼                     ▼  │
│                   ┌─────────────────┐  ┌─────────────────┐  ┌───────────┐  │
│                   │   Prometheus    │  │    Promtail     │  │   Sentry  │  │
│                   │ :9090           │  │  (log shipper)  │  │  (cloud)  │  │
│                   │                 │  │                 │  │           │  │
│                   │ Pulls /metrics  │  │ Tails log files │  │ Receives  │  │
│                   │ every 15s       │  │ → pushes to Loki│  │ errors    │  │
│                   └────────┬────────┘  └────────┬────────┘  └───────────┘  │
│                            │                    │                          │
│                            │ evaluate           │ push                     │
│                            │ rules              │ logs                     │
│                            ▼                    ▼                          │
│                   ┌─────────────────┐  ┌─────────────────┐                 │
│                   │  Alertmanager   │  │      Loki       │                 │
│                   │ :9093           │  │ :3100           │                 │
│                   │                 │  │                 │                 │
│                   │ Routes alerts   │  │ Stores logs     │                 │
│                   │ to Slack        │  │ with labels     │                 │
│                   └────────┬────────┘  └────────┬────────┘                 │
│                            │                    │                          │
│                            │ notify             │ query                    │
│                            ▼                    ▼                          │
│                   ┌─────────────────┐  ┌─────────────────┐                 │
│                   │     Slack       │  │    Grafana      │                 │
│                   │ #alerts-*       │  │ :3000           │                 │
│                   │                 │  │                 │                 │
│                   │ Receives alert  │  │ Dashboards &    │                 │
│                   │ notifications   │  │ log exploration │                 │
│                   └─────────────────┘  └─────────────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Prometheus

### What Is Prometheus?

Prometheus is an open-source monitoring system that collects metrics from your applications. It uses a "pull model" - meaning it scrapes (pulls) data from your app, rather than your app pushing data to it.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMETHEUS WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Application exposes metrics                                        │
│  ─────────────────────────────────────                                      │
│                                                                             │
│      Django App                                                             │
│          │                                                                  │
│          │ Exposes /metrics endpoint                                        │
│          ▼                                                                  │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ GET /metrics                                    │                   │
│      │                                                 │                   │
│      │ # HELP django_http_requests_total              │                   │
│      │ # TYPE django_http_requests_total counter      │                   │
│      │ django_http_requests_total{method="GET"} 1234  │                   │
│      │                                                 │                   │
│      │ # HELP django_db_query_duration_seconds         │                   │
│      │ django_db_query_duration_seconds 0.005          │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 2: Prometheus scrapes (pulls) metrics                                 │
│  ──────────────────────────────────────────                                 │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Prometheus                                      │                   │
│      │                                                 │                   │
│      │ Every 15 seconds:                               │                   │
│      │ 1. HTTP GET to obs-django:9000/metrics         │                   │
│      │ 2. Parse response                               │                   │
│      │ 3. Store in TSDB                                │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 3: Prometheus stores metrics                                          │
│  ─────────────────────────────────                                          │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Time Series Database (TSDB)                     │                   │
│      │                                                 │                   │
│      │ Metric Name          Timestamp    Value         │                   │
│      │ ─────────────────────────────────────────────  │                   │
│      │ django_http_...total  10:00:00     1234        │                   │
│      │ django_http_...total  10:00:15     1235        │                   │
│      │ django_http_...total  10:00:30     1236        │                   │
│      │ django_db_...seconds  10:00:00     0.005       │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 4: Prometheus evaluates alert rules                                   │
│  ─────────────────────────────────────────                                  │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Alert Rules                                     │                   │
│      │                                                 │                   │
│      │ - alert: DjangoDown                             │                   │
│      │   expr: up{job="django"} == 0                   │                   │
│      │   for: 10s                                      │                   │
│      │                                                 │                   │
│      │ Every 15 seconds:                               │                   │
│      │ 1. Evaluate expression                          │                   │
│      │ 2. If true for 10s → send alert                │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration Explained

**File:** `prometheus/prometheus.yml`

```yaml
# Global settings
global:
  scrape_interval: 15s    # How often to scrape targets (default: 15 seconds)
  evaluation_interval: 15s  # How often to evaluate alert rules (default: 15 seconds)

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ["obs-alertmanager:9093"]  # Where to send alerts

# Alert rules location
rule_files:
  - /etc/prometheus/rules/*.yml  # Load all .yml files in this directory

# What to scrape
scrape_configs:

  # Job 1: Prometheus itself (self-monitoring)
  - job_name: "prometheus"           # Job name
    static_configs:
      - targets: ["localhost:9090"]  # Scrape itself

  # Job 2: Django application
  - job_name: "django"
    static_configs:
      - targets: ["obs-django:9000"]  # Docker container name and port
    metrics_path: /metrics            # Endpoint to scrape

  # Job 3: Node Exporter (host metrics)
  - job_name: "node"
    static_configs:
      - targets: ["obs-node-exporter:9100"]

  # Job 4: Loki (log system metrics)
  - job_name: "loki"
    static_configs:
      - targets: ["obs-loki:3100"]
    metrics_path: /metrics

  # Job 5: Grafana (UI metrics)
  - job_name: "grafana"
    static_configs:
      - targets: ["obs-grafana:3000"]
    metrics_path: /metrics
```

### Key Concepts

| Concept | Meaning |
|---------|---------|
| **Scrape** | Pulling metrics from a target |
| **Scrape interval** | How often to pull (15s) |
| **Target** | Where to scrape (container:port) |
| **Job** | Group of targets |
| **Metric** | A measurement (e.g., request count) |
| **Label** | Metadata for filtering (e.g., method=GET) |
| **TSDB** | Time Series Database (storage) |
| **Alert rule** | Condition that triggers alert |

### How to Test

```bash
# Check if Prometheus is running
curl http://localhost:9090/-/healthy

# Query a metric
curl 'http://localhost:9090/api/v1/query?query=up'

# View all targets
curl http://localhost:9090/api/v1/targets | jq

# View alert rules
curl http://localhost:9090/api/v1/rules | jq
```

### Official Documentation

- [Prometheus Docs](https://prometheus.io/docs/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)

---

## Loki

### What Is Loki?

Loki is a log aggregation system designed to be cost-effective and easy to operate. Unlike Elasticsearch, Loki only indexes metadata (labels), not the full log text. Think of it as "Prometheus, but for logs."

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOKI WORKFLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Promtail pushes logs                                               │
│  ─────────────────────────────                                              │
│                                                                             │
│      Promtail                                                               │
│          │                                                                  │
│          │ HTTP POST to /loki/api/v1/push                                   │
│          │                                                                  │
│          │ {                                                                │
│          │   "streams": [{                                                  │
│          │     "stream": {"app": "django", "level": "INFO"},                │
│          │     "values": [["1773536578000000000", "GET /todo/ 200"]]        │
│          │   }]                                                             │
│          │ }                                                                │
│          ▼                                                                  │
│                                                                             │
│  Step 2: Loki receives and stores                                           │
│  ──────────────────────────────                                             │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Loki                                            │                   │
│      │                                                 │                   │
│      │ 1. Parse request                                │                   │
│      │ 2. Extract labels (app, level)                  │                   │
│      │ 3. Store log line                               │                   │
│      │ 4. Update index                                 │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 3: Loki stores data                                                   │
│  ────────────────────────                                                   │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Storage Structure                              │                   │
│      │                                                 │                   │
│      │ INDEX (Labels)                                  │                   │
│      │ ─────────────────────────────────────────────  │                   │
│      │ {app="django"} → chunk_001                      │                   │
│      │ {app="django", level="ERROR"} → chunk_002      │                   │
│      │ {app="django", log_type="access"} → chunk_003  │                   │
│      │                                                 │                   │
│      │ CHUNKS (Actual log data)                        │                   │
│      │ ─────────────────────────────────────────────  │                   │
│      │ chunk_001:                                      │                   │
│      │   [1773536578000000000] "GET /todo/ 200"       │                   │
│      │   [1773536578000000001] "POST /todo/ 302"      │                   │
│      │                                                 │                   │
│      │ chunk_002:                                      │                   │
│      │   [1773536578000000002] "Error: DB timeout"     │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 4: Loki serves queries                                                │
│  ──────────────────────────                                                 │
│                                                                             │
│      Grafana → GET /loki/api/v1/query?query={app="django"}                 │
│                                                                             │
│      Response:                                                              │
│      {                                                                      │
│        "status": "success",                                                 │
│        "data": {                                                            │
│          "result": [{                                                       │
│            "stream": {"app": "django", "level": "INFO"},                    │
│            "values": [["1773536578000000000", "GET /todo/ 200"]]            │
│          }]                                                                 │
│        }                                                                    │
│      }                                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration Explained

**File:** `loki/loki-config.yml`

```yaml
# Don't require authentication (development mode)
auth_enabled: false

# Server settings
server:
  http_listen_port: 3100  # Port for HTTP API

# Common configuration
common:
  instance_addr: 127.0.0.1  # Instance address
  path_prefix: /loki          # Root directory for Loki data
  storage:
    filesystem:
      chunks_directory: /loki/chunks   # Where log data is stored
      rules_directory: /loki/rules     # Where recording rules are stored
  replication_factor: 1                  # Number of replicas (1 for single node)
  ring:
    kvstore:
      store: inmemory  # Store ring info in memory

# Schema configuration (how data is organized)
schema_config:
  configs:
    - from: 2024-01-01          # Start date for this schema
      store: tsdb                # Storage backend
      object_store: filesystem   # Where to store objects
      schema: v12                # Schema version
      index:
        prefix: index_           # Index file prefix
        period: 24h              # Rotate index every 24 hours

# Rate limits
limits_config:
  retention_period: 30d         # Keep logs for 30 days
  ingestion_rate_mb: 16         # Max ingestion rate (MB/s)
  ingestion_burst_size_mb: 32   # Max burst size (MB)
```

### Key Concepts

| Concept | Meaning |
|---------|---------|
| **Stream** | A set of logs with same labels |
| **Labels** | Metadata tags (app=django, level=ERROR) |
| **Chunks** | Compressed log data |
| **Index** | Label-based search index |
| **LogQL** | Loki query language |
| **Push API** | HTTP POST to ingest logs |
| **Query API** | HTTP GET to search logs |

### How to Test

```bash
# Check if Loki is ready
curl http://localhost:3100/ready

# Push a test log
curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test"},"values":[["1773536578000000000","test"]]}]}'

# Query logs
curl 'http://localhost:3100/loki/api/v1/query?query={app="test"}'

# List labels
curl http://localhost:3100/loki/api/v1/label | jq
```

### Official Documentation

- [Loki Docs](https://grafana.com/docs/loki/latest/)
- [LogQL Query Language](https://grafana.com/docs/loki/latest/logql/)
- [Loki Configuration](https://grafana.com/docs/loki/latest/configure/)

---

## Promtail

### What Is Promtail?

Promtail is an agent that reads log files and sends them to Loki. Think of it as a "log mailman" - it picks up logs and delivers them.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMTAIL WORKFLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Watch log files                                                    │
│  ─────────────────────────                                                  │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ /app/logs/django.log                            │                   │
│      │                                                 │                   │
│      │ {"asctime":"2026-03-15",                        │                   │
│      │  "levelname":"INFO",                            │                   │
│      │  "name":"django",                               │                   │
│      │  "message":"GET /todo/ 200"}                    │                   │
│      │                                                 │                   │
│      │ ← Promtail watches this file (tail -f)         │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 2: Parse JSON                                                         │
│  ──────────────────                                                         │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Pipeline Stages                                 │                   │
│      │                                                 │                   │
│      │ Input JSON:                                     │                   │
│      │ {"levelname":"INFO","name":"django",            │                   │
│      │  "message":"GET /todo/ 200"}                    │                   │
│      │                                                 │                   │
│      │ After json parsing:                             │                   │
│      │ level = "INFO"                                  │                   │
│      │ logger = "django"                               │                   │
│      │ message = "GET /todo/ 200"                      │                   │
│      │                                                 │                   │
│      │ After labels extraction:                        │                   │
│      │ Labels: {app="django", env="dev", level="INFO"} │                   │
│      │ Log line: "GET /todo/ 200"                      │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 3: Push to Loki                                                       │
│  ────────────────────                                                       │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ HTTP POST                                       │                   │
│      │                                                 │                   │
│      │ URL: http://obs-loki:3100/loki/api/v1/push     │                   │
│      │                                                 │                   │
│      │ Body:                                           │                   │
│      │ {                                               │                   │
│      │   "streams": [{                                 │                   │
│      │     "stream": {                                 │                   │
│      │       "app": "django",                          │                   │
│      │       "env": "dev",                             │                   │
│      │       "level": "INFO"                           │                   │
│      │     },                                          │                   │
│      │     "values": [                                 │                   │
│      │       ["1773536578000000000",                   │                   │
│      │        "GET /todo/ 200"]                        │                   │
│      │     ]                                           │                   │
│      │   }]                                            │                   │
│      │ }                                               │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 4: Track position                                                     │
│  ──────────────────────                                                     │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ positions.yaml                                  │                   │
│      │                                                 │                   │
│      │ /var/log/django/django.log:                     │                   │
│      │   value: 12345   ← Last byte position read     │                   │
│      │                                                 │                   │
│      │ /var/log/django/access.log:                     │                   │
│      │   value: 67890   ← Last byte position read     │                   │
│      │                                                 │                   │
│      │ This ensures Promtail doesn't re-send logs     │                   │
│      │ after restart                                   │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration Explained

**File:** `promtail/promtail-config.yml`

```yaml
# Server settings
server:
  http_listen_port: 9080    # Port for metrics endpoint
  grpc_listen_port: 0       # Disable gRPC (not needed)

# Position tracking (remembers where it left off)
positions:
  filename: /tmp/positions.yaml  # File to store read positions

# Where to send logs
clients:
  - url: http://obs-loki:3100/loki/api/v1/push  # Loki push endpoint

# What files to watch
scrape_configs:

  # Job 1: Django application logs (JSON format)
  - job_name: django                # Job name
    static_configs:
      - targets:
          - localhost               # (required but ignored)
        labels:
          app: django               # Label: app=django
          env: dev                  # Label: env=dev
          __path__: /var/log/django/django.log  # File to watch
    pipeline_stages:
      - json:                       # Parse as JSON
          expressions:
            level: levelname        # Extract "levelname" field → "level" label
            logger: name            # Extract "name" field → "logger" label
            message: message        # Extract "message" field
      - labels:                     # Convert to Loki labels
          level:                    # Make "level" a searchable label
          logger:                   # Make "logger" a searchable label

  # Job 2: Gunicorn access logs
  - job_name: gunicorn_access
    static_configs:
      - targets:
          - localhost
        labels:
          app: django
          log_type: access          # Label: log_type=access
          env: dev
          __path__: /var/log/django/access.log
    pipeline_stages:
      - labels:
          log_type:

  # Job 3: Gunicorn error logs
  - job_name: gunicorn_error
    static_configs:
      - targets:
          - localhost
        labels:
          app: django
          log_type: error           # Label: log_type=error
          level: ERROR              # Label: level=ERROR
          env: dev
          __path__: /var/log/django/error.log
    pipeline_stages:
      - labels:
          level:
          log_type:
```

### Key Concepts

| Concept | Meaning |
|---------|---------|
| **`__path__`** | File path to watch |
| **`targets`** | Required but ignored for file watching |
| **`labels`** | Metadata tags added to logs |
| **`pipeline_stages`** | How to process log lines |
| **`json`** | Parse JSON format |
| **`positions.yaml`** | Tracks last read position |

### How to Test

```bash
# Check Promtail logs
docker logs obs-promtail --tail 20

# Check targets
curl http://localhost:9080/targets | jq

# Verify tailing
docker logs obs-promtail | grep "tail routine"
```

### Official Documentation

- [Promtail Docs](https://grafana.com/docs/loki/latest/send-data/promtail/)
- [Pipeline Stages](https://grafana.com/docs/loki/latest/send-data/promtail/configuration/#pipeline_stages)

---

## Alertmanager

### What Is Alertmanager?

Alertmanager receives alerts from Prometheus and routes them to different notification channels (Slack, email, etc.). Think of it as a "dispatcher" that decides where to send messages.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ALERTMANAGER WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Receive alert from Prometheus                                      │
│  ─────────────────────────────────────                                      │
│                                                                             │
│      Prometheus                                                             │
│          │                                                                  │
│          │ HTTP POST to /api/v1/alerts                                      │
│          │                                                                  │
│          │ [                                                                │
│          │   {                                                              │
│          │     "labels": {                                                  │
│          │       "alertname": "DjangoDown",                                 │
│          │       "severity": "critical",                                    │
│          │       "category": "http"                                         │
│          │     },                                                           │
│          │     "annotations": {                                             │
│          │       "summary": "Django is DOWN"                                │
│          │     }                                                            │
│          │   }                                                              │
│          │ ]                                                                │
│          ▼                                                                  │
│                                                                             │
│  Step 2: Group alerts                                                       │
│  ────────────────────                                                       │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Alertmanager                                    │                   │
│      │                                                 │                   │
│      │ group_by: ["alertname", "category"]             │                   │
│      │ group_wait: 30s                                 │                   │
│      │                                                 │                   │
│      │ If multiple alerts come within 30s:             │                   │
│      │ - Group by alertname and category               │                   │
│      │ - Send one notification per group               │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 3: Route to receiver                                                  │
│  ───────────────────────                                                    │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Routing Rules                                   │                   │
│      │                                                 │                   │
│      │ If category=db     → send to #alerts-db        │                   │
│      │ If category=http   → send to #alerts-http      │                   │
│      │ If category=latency→ send to #alerts-latency   │                   │
│      │ If category=infra  → send to #alerts-infra     │                   │
│      │ Otherwise          → send to #alerts           │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 4: Send to Slack                                                      │
│  ────────────────────                                                       │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Slack Message                                   │                   │
│      │                                                 │                   │
│      │ 🔥 [FIRING] DjangoDown                          │                   │
│      │                                                 │                   │
│      │ 🚨 CRITICAL — Django is DOWN                    │                   │
│      │                                                 │                   │
│      │ 📋 Reason: App unreachable for 10s             │                   │
│      │ 🏷️ Alert: `DjangoDown`                         │                   │
│      │ 🔖 Category: `http`                            │                   │
│      │ 🕐 Started: 2026-03-15 10:30:00 UTC           │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration Explained

**File:** `alertmanager/alertmanager.yml`

```yaml
# Global settings
global:
  resolve_timeout: 5m           # Wait 5 minutes before marking as resolved
  slack_api_url: "PLACEHOLDER"  # Replaced at runtime with SLACK_WEBHOOK_URL

# Routing configuration
route:
  group_by: ["alertname", "category"]  # Group alerts by name and category
  group_wait: 30s                       # Wait 30s to collect alerts
  group_interval: 5m                    # Wait 5m between groups
  repeat_interval: 12h                  # Repeat alert every 12 hours
  receiver: "slack-default"             # Default receiver
  routes:                               # Specific routing rules
    - match:
        category: db                    # If category=db
      receiver: "slack-db"              # Send to #alerts-db

    - match:
        alertname: DjangoDown           # If DjangoDown
        category: http
      receiver: "slack-http"
      repeat_interval: 10m              # Repeat every 10 minutes

    - match:
        category: http                  # Other HTTP alerts
      receiver: "slack-http"

    - match:
        category: latency
      receiver: "slack-latency"

    - match:
        category: infrastructure
      receiver: "slack-infra"

# Receivers (notification targets)
receivers:
  - name: "slack-default"
    slack_configs:
      - channel: "#alerts"
        username: "Observability Bot"
        icon_emoji: ":bell:"
        color: '{{ if eq .Status "firing" }}#FF0000{{ else }}#36A64F{{ end }}'
        title: '[{{ .Status | toUpper }}] {{ .GroupLabels.alertname }}'
        text: |
          {{ range .Alerts }}
          {{ .Annotations.summary }}
          {{ end }}
        send_resolved: true

# Inhibit rules (suppress lower severity if higher is active)
inhibit_rules:
  - source_match:
      severity: "critical"
    target_match:
      severity: "warning"
    equal: ["alertname"]
```

### Key Concepts

| Concept | Meaning |
|---------|---------|
| **Receiver** | Where to send (Slack channel) |
| **Route** | How to match alerts to receivers |
| **Group** | Combine similar alerts |
| **group_wait** | Wait before sending |
| **repeat_interval** | How often to repeat |
| **inhibit_rule** | Suppress lower severity alerts |

### How to Test

```bash
# Check Alertmanager status
curl http://localhost:9093/api/v1/status | jq

# View active alerts
curl http://localhost:9093/api/v1/alerts | jq

# Send test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"Test","severity":"warning","category":"http"},"annotations":{"summary":"Test alert"}}]'
```

### Official Documentation

- [Alertmanager Docs](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Configuration](https://prometheus.io/docs/alerting/latest/configuration/)
- [Routing](https://prometheus.io/docs/alerting/latest/configuration/#route)

---

## Grafana

### What Is Grafana?

Grafana is a visualization platform that creates dashboards from your data. Think of it as a "TV" that shows channels from Prometheus and Loki.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GRAFANA WORKFLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Connect to datasources                                             │
│  ────────────────────────────────                                           │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Grafana                                         │                   │
│      │                                                 │                   │
│      │ Datasources:                                    │                   │
│      │ - Prometheus: http://obs-prometheus:9090        │                   │
│      │ - Loki: http://obs-loki:3100                    │                   │
│      │                                                 │                   │
│      │ Configured in:                                  │                   │
│      │ grafana/provisioning/datasources/datasources.yml│                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 2: Query datasources                                                  │
│  ───────────────────────                                                    │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ PromQL (Prometheus)                             │                   │
│      │                                                 │                   │
│      │ rate(django_http_requests_total[5m])            │                   │
│      │                                                 │                   │
│      │ This calculates requests per second over 5 min  │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ LogQL (Loki)                                    │                   │
│      │                                                 │                   │
│      │ {app="django", level="ERROR"}                   │                   │
│      │                                                 │                   │
│      │ This returns all error logs from Django         │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 3: Display dashboards                                                 │
│  ────────────────────────                                                   │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Dashboard Panels                               │                   │
│      │                                                 │                   │
│      │ ┌──────────────┐  ┌──────────────┐             │                   │
│      │ │ Request Rate │  │ Error Rate   │             │                   │
│      │ │    ┌───┐     │  │    ┌───┐     │             │                   │
│      │ │    │   │     │  │    │   │     │             │                   │
│      │ │    │   │     │  │    │   │     │             │                   │
│      │ │    └───┘     │  │    └───┘     │             │                   │
│      │ │  0.5 req/s   │  │  0.01%       │             │                   │
│      │ └──────────────┘  └──────────────┘             │                   │
│      │                                                 │                   │
│      │ ┌──────────────┐  ┌──────────────┐             │                   │
│      │ │ P95 Latency  │  │ Recent Logs  │             │                   │
│      │ │    ┌───┐     │  │ INFO: GET    │             │                   │
│      │ │    │   │     │  │ ERROR: ...   │             │                   │
│      │ │    └───┘     │  │              │             │                   │
│      │ │   45.2ms     │  │              │             │                   │
│      │ └──────────────┘  └──────────────┘             │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuration Explained

**File:** `grafana/provisioning/datasources/datasources.yml`

```yaml
# Datasource provisioning format
apiVersion: 1

# Delete old datasources on startup (clean slate)
deleteDatasources:
  - name: Prometheus
    orgId: 1
  - name: Loki
    orgId: 1

# Define datasources
datasources:

  # Prometheus datasource
  - name: Prometheus                    # Display name
    type: prometheus                    # Datasource type
    uid: prometheus                     # Unique identifier
    orgId: 1                            # Organization ID
    access: proxy                       # Access mode (proxy = through Grafana)
    url: http://obs-prometheus:9090    # Prometheus URL
    isDefault: true                     # Default datasource
    editable: false                     # Can't edit in UI
    version: 1                          # Version number

  # Loki datasource
  - name: Loki
    type: loki
    uid: loki
    orgId: 1
    access: proxy
    url: http://obs-loki:3100
    isDefault: false
    editable: false
    version: 1
    jsonData:
      maxLines: 1000                    # Max lines to display
```

### Key Concepts

| Concept | Meaning |
|---------|---------|
| **Datasource** | Data source connection |
| **Panel** | Dashboard widget |
| **Dashboard** | Collection of panels |
| **PromQL** | Prometheus query language |
| **LogQL** | Loki query language |
| **Provisioning** | Auto-configure on startup |

### How to Test

```bash
# Check Grafana health
curl http://localhost:3000/api/health

# List datasources
curl -u admin:admin http://localhost:3000/api/datasources | jq

# Query Prometheus via Grafana
curl -u admin:admin 'http://localhost:3000/api/datasources/uid/prometheus/api/v1/query?query=up'
```

### Official Documentation

- [Grafana Docs](https://grafana.com/docs/grafana/latest/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL](https://grafana.com/docs/loki/latest/logql/)

---

## Node Exporter

### What Is Node Exporter?

Node Exporter collects host-level metrics (CPU, memory, disk, network). Think of it as a "stethoscope" for your server.

### How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NODE EXPORTER WORKFLOW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1: Read host metrics                                                  │
│  ─────────────────────────                                                  │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ Node Exporter                                   │                   │
│      │                                                 │                   │
│      │ Reads from:                                     │                   │
│      │ - /proc (CPU, memory, network)                  │                   │
│      │ - /sys (system information)                     │                   │
│      │ - / (disk usage)                                │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 2: Expose metrics                                                     │
│  ──────────────────────                                                     │
│                                                                             │
│      ┌─────────────────────────────────────────────────┐                   │
│      │ GET :9100/metrics                               │                   │
│      │                                                 │                   │
│      │ # HELP node_cpu_seconds_total                   │                   │
│      │ node_cpu_seconds_total{cpu="0",mode="idle"}     │                   │
│      │                                                 │                   │
│      │ # HELP node_memory_MemTotal_bytes               │                   │
│      │ node_memory_MemTotal_bytes 8589934592           │                   │
│      │                                                 │                   │
│      │ # HELP node_filesystem_avail_bytes              │                   │
│      │ node_filesystem_avail_bytes{mountpoint="/"}     │                   │
│      │                                                 │                   │
│      │ # HELP node_network_receive_bytes_total         │                   │
│      │ node_network_receive_bytes_total{device="eth0"} │                   │
│      └─────────────────────────────────────────────────┘                   │
│                                                                             │
│  Step 3: Prometheus scrapes                                                 │
│  ────────────────────────                                                   │
│                                                                             │
│      Prometheus → GET :9100/metrics → Store in TSDB                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Docker Configuration Explained

```yaml
obs-node-exporter:
  image: prom/node-exporter:latest
  pid: host                      # Share host's PID namespace
  volumes:
    - /proc:/host/proc:ro        # Mount host /proc (CPU, memory, processes)
    - /sys:/host/sys:ro          # Mount host /sys (system info)
    - /:/rootfs:ro               # Mount host filesystem (disk usage)
  command:
    - "--path.procfs=/host/proc"                                        # Where to read proc
    - "--path.sysfs=/host/sys"                                          # Where to read sys
    - "--path.rootfs=/rootfs"                                           # Where to read rootfs
    - "--collector.filesystem.mount-points-exclude=^/(sys|proc|..."     # Exclude system mounts
```

### Key Metrics

| Metric | Description |
|--------|-------------|
| `node_cpu_seconds_total` | CPU usage by mode |
| `node_memory_MemAvailable_bytes` | Available memory |
| `node_memory_MemTotal_bytes` | Total memory |
| `node_filesystem_avail_bytes` | Available disk space |
| `node_network_receive_bytes_total` | Network traffic received |

### How to Test

```bash
# View all metrics
curl http://localhost:9100/metrics

# View CPU metrics
curl http://localhost:9100/metrics | grep node_cpu

# View memory metrics
curl http://localhost:9100/metrics | grep node_memory
```

### Official Documentation

- [Node Exporter GitHub](https://github.com/prometheus/node_exporter)
- [Collectors](https://github.com/prometheus/node_exporter#collectors)

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE DATA FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  METRICS (Pull Model)                                                       │
│  ─────────────────────                                                      │
│                                                                             │
│  Django → GET /metrics → Prometheus → Alertmanager → Slack                  │
│                 ↓                                                           │
│            Grafana                                                           │
│                                                                             │
│  LOGS (Push Model)                                                          │
│  ─────────────────                                                          │
│                                                                             │
│  Django → Log File → Promtail → POST /loki/api/v1/push → Loki             │
│                                                      ↓                      │
│                                                  Grafana                    │
│                                                                             │
│  HOST METRICS (Pull Model)                                                  │
│  ─────────────────────────                                                  │
│                                                                             │
│  Host System → Node Exporter → GET /metrics → Prometheus                   │
│                                                     ↓                       │
│                                                 Grafana                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Tool | Port | URL | Purpose |
|------|------|-----|---------|
| Prometheus | 9090 | http://localhost:9090 | Metrics collection |
| Loki | 3100 | http://localhost:3100 | Log storage |
| Alertmanager | 9093 | http://localhost:9093 | Alert routing |
| Grafana | 3000 | http://localhost:3000 | Dashboards |
| Node Exporter | 9100 | http://localhost:9100 | Host metrics |
| pgAdmin | 5050 | http://localhost:5050 | DB admin |
| Django | 9000 | http://localhost:9000 | Application |

---

## Related Documentation

- [Getting Started](getting-started.md)
- [Architecture Overview](architecture.md)
- [Tutorial](tutorial/setup.md)
- [API Reference](reference/api.md)
- [Troubleshooting](reference/troubleshooting.md)
