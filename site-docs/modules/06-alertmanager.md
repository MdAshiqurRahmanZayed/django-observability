# Alertmanager

## Overview

Alertmanager handles alerts sent by Prometheus. It receives alerts from Prometheus, deduplicates, groups, and routes them to the correct receiver (Slack, email, etc.) based on configured rules.

## Description

Alertmanager is responsible for:
- Receiving alerts from Prometheus
- Grouping similar alerts
- Routing alerts to appropriate receivers
- Managing alert lifecycle (firing/resolved)
- Sending notifications to Slack

In this stack, Alertmanager:
- Receives alerts from Prometheus
- Routes alerts to different Slack channels
- Groups alerts by category
- Sends formatted notifications

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ALERTMANAGER IN STACK                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ALERT FLOW                                                                │
│   ───────────                                                               │
│                                                                             │
│   ┌──────────────┐      ALERTS       ┌──────────────┐       NOTIFICATIONS   │
│   │  Prometheus  │ ────────────────▶ │  Alertmanager│───▶.  Slack Channels  │
│   │   (rules)    │  POST /api/v1/    │    :9093     │     #alerts           │
│   │              │                   │              │     #alerts-db        │
│   └──────────────┘                   └──────────────┘     #alerts-http      │
│                                              │            #alerts-latency   │
│                                              │            #alerts-infra     │
│                                              │                              │
│   ┌──────────────────────────────────────────┴─────────────────────────┐    │
│   │                      ALERT ROUTING                                 │    │
│   │                                                                    │    │
│   │   category=db      ──▶ #alerts-db                                  │    │
│   │   category=http   ──▶ #alerts-http                                 │    │
│   │   category=latency ──▶ #alerts-latency                             │    │
│   │   category=infrastructure ──▶ #alerts-infra                        │    │
│   │   (default)       ──▶ #alerts                                      │    │
│   └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Alert Routing | Alertmanager | Latest |
| Notifications | Slack | Via webhook |

## Docker Configuration

### docker-compose.yml

```yaml
obs-alertmanager:
  image: prom/alertmanager:latest
  container_name: obs-alertmanager
  restart: unless-stopped
  ports:
    - "9093:9093"
  volumes:
    - ./../alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml.tmpl:ro
    - alertmanager_data:/alertmanager
  entrypoint: ["/bin/sh", "-c"]
  command:
    - "sed 's|SLACK_WEBHOOK_URL_PLACEHOLDER|'$$SLACK_WEBHOOK_URL'|g' /etc/alertmanager/alertmanager.yml.tmpl > /tmp/alertmanager.yml && /bin/alertmanager --config.file=/tmp/alertmanager.yml --storage.path=/alertmanager"
  environment:
    SLACK_WEBHOOK_URL: ${SLACK_WEBHOOK_URL}
  networks:
    - observability_network
```

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
  routes:
    - match:
        category: db
      receiver: "slack-db"
    - match:
        category: http
      receiver: "slack-http"
    - match:
        category: latency
      receiver: "slack-latency"
    - match:
        category: infrastructure
      receiver: "slack-infra"

receivers:
  - name: "slack-default"
    slack_configs:
      - channel: "#alerts"
        send_resolved: true
  - name: "slack-db"
    slack_configs:
      - channel: "#alerts-db"
        send_resolved: true
  - name: "slack-http"
    slack_configs:
      - channel: "#alerts-http"
        send_resolved: true
  - name: "slack-latency"
    slack_configs:
      - channel: "#alerts-latency"
        send_resolved: true
  - name: "slack-infra"
    slack_configs:
      - channel: "#alerts-infra"
        send_resolved: true
```

## Network Access

| Access | URL |
|--------|-----|
| External (host) | http://localhost:9093 |
| Internal (Docker) | http://obs-alertmanager:9093 |

## Alert Routing

### How It Works

```
1. Prometheus evaluates alert rules every 15s
        │
        ▼
2. Alert condition met → Prometheus sends to Alertmanager
   POST http://obs-alertmanager:9093/api/v1/alerts
        │
        ▼
3. Alertmanager receives and:
   a) Deduplicates (groups identical alerts)
   b) Waits group_wait (30s) for more alerts
   c) Sends to configured receiver
        │
        ▼
4. Slack receives formatted notification
```

### Routing Configuration

| Category | Slack Channel | Alert Examples |
|----------|---------------|----------------|
| db | #alerts-db | DBHighErrorRate, DBSlowQueries |
| http | #alerts-http | DjangoDown, Django5xxError |
| latency | #alerts-latency | HighP95Latency, HighP99Latency |
| infrastructure | #alerts-infra | HighCPUUsage, HighMemoryUsage |

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Group** | Group alerts by label (alertname, category) |
| **group_wait** | Wait 30s to collect alerts before sending |
| **group_interval** | Send new alerts every 5m |
| **repeat_interval** | Repeat resolved alert after 12h |

## Useful Commands

### Container Management

```bash
# Restart Alertmanager
docker compose -f django_app/docker-compose.yml restart obs-alertmanager

# View logs
docker logs -f obs-alertmanager

# Access shell
docker exec -it obs-alertmanager /bin/sh
```

### Check Alerts

```bash
# View active alerts
curl http://localhost:9093/api/v1/alerts | jq

# View alert status
curl http://localhost:9093/api/v1/status | jq
```

### Test Configuration

```bash
# Validate config
docker exec obs-alertmanager amtool check-config /etc/alertmanager/alertmanager.yml

# Check routing
curl http://localhost:9093/api/v1/status | jq '.config.route'
```

## Expected Output

### Active Alerts

```bash
$ curl http://localhost:9093/api/v1/alerts | jq

[
  {
    "labels": {
      "alertname": "DjangoDown",
      "category": "http",
      "severity": "critical"
    },
    "annotations": {
      "summary": "Django is DOWN",
      "description": "Django app has been unreachable for more than 10 seconds"
    },
    "state": "firing",
    "activeAt": "2026-03-15T10:30:00Z"
  }
]
```

### Alertmanager Status

```bash
$ curl http://localhost:9093/api/v1/status | jq

{
  "config": {
    "route": {
      "group_by": ["alertname", "category"],
      "group_wait": "30s",
      "group_interval": "5m",
      "repeat_interval": "12h"
    }
  },
  "uptime": "2026-03-15T10:00:00Z",
  "version": "..."
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/alerts` | POST | Receive alerts from Prometheus |
| `/api/v1/alerts` | GET | List active alerts |
| `/api/v1/status` | GET | Alertmanager status |
| `/metrics` | GET | Prometheus metrics |
| `/healthy` | GET | Health check |

## Health Checks

```bash
# Health check
curl -f http://localhost:9093/healthy || echo "Alertmanager is down"

# Check status
curl http://localhost:9093/api/v1/status | jq

# Check alerts
curl http://localhost:9093/api/v1/alerts | jq 'length'
```

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| alertmanager.yml | alertmanager/alertmanager.yml | Routing configuration |

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Prometheus | Receive alerts :9093 | Alert source |
| Slack | Webhook URL | Notification destination |

## Alert Categories

| Category | Severity | Example Alerts |
|----------|-----------|----------------|
| db | critical, warning | DBHighErrorRate, DBSlowQueries |
| http | critical, warning | DjangoDown, Django5xxError |
| latency | critical, warning | HighP95Latency, HighP99Latency |
| infrastructure | critical, warning | HighCPUUsage, HighMemoryUsage |

## Troubleshooting

### Alerts Not Received

```bash
# Check Prometheus config
curl http://localhost:9090/api/v1/status/config | jq '.data.yaml'

# Check Prometheus knows Alertmanager
curl http://localhost:9090/api/v1/alertmanagers | jq

# Check Alertmanager logs
docker logs obs-alertmanager
```

### Slack Notifications Not Working

```bash
# Check webhook URL is set
docker exec obs-alertmanager env | grep SLACK

# Test webhook manually
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert"}' \
  $SLACK_WEBHOOK_URL

# Check Alertmanager receiver config
curl http://localhost:9093/api/v1/status | jq '.config.receivers'
```

### Alert Storms

```bash
# Adjust grouping
# Edit alertmanager.yml:
#   group_wait: 30s  (increase to reduce storm)
#   group_interval: 5m  (increase to reduce duplicates)

# Reload config
docker exec obs-alertmanager kill -HUP 1
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-alertmanager

# Stop
docker compose -f django_app/docker-compose.yml stop obs-alertmanager

# Restart
docker compose -f django_app/docker-compose.yml restart obs-alertmanager

# View logs
docker logs -f obs-alertmanager
```

### URLs

| Service | URL |
|---------|-----|
| Alertmanager UI | http://localhost:9093 |
| Alerts | http://localhost:9093/#/alerts |
| Status | http://localhost:9093/api/v1/status |

### Key Ports

| Port | Service |
|------|---------|
| 9093 | Alertmanager UI/API |

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| group_wait | 30s | Wait before sending first alert |
| group_interval | 5m | Wait between alert groups |
| repeat_interval | 12h | Repeat resolved alerts |

### Environment Variables

| Variable | Description |
|----------|-------------|
| SLACK_WEBHOOK_URL | Slack webhook URL for notifications |

---

## Related Documentation

- [Prometheus](./02-prometheus.md) - Alert rules source
- [Grafana](./03-grafana.md) - Alert visualization
