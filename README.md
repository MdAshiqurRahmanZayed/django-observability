# Django Observability

A full-stack Django observability setup with metrics, logs, alerting, and error tracking.

## Stack & Ports

| Service        | Container          | Port          | Purpose                        |
|----------------|--------------------|---------------|--------------------------------|
| Django         | obs-django         | internal 9000 | App (no direct access)         |
| Nginx          | obs-nginx          | 80            | Entry point / reverse proxy    |
| PostgreSQL     | obs-postgres       | internal 5432 | Database                       |
| Prometheus     | obs-prometheus     | 9090          | Metrics scraper & alert rules  |
| Alertmanager   | obs-alertmanager   | 9093          | Alert routing → Slack          |
| Loki           | obs-loki           | 3100          | Log storage                    |
| Promtail       | obs-promtail       | internal      | Log shipper                    |
| Grafana        | obs-grafana        | 3000          | Dashboards                     |
| Node Exporter  | obs-node-exporter  | internal 9100 | Host metrics                   |
| Sentry         | sentry.io (cloud)  | —             | Error tracking & tracing       |

## Architecture

```
Browser
   |
   v
Nginx :80
   |
   |---> /static  -> staticfiles volume
   |---> /media   -> mediafiles volume
   +---> /        -> obs-django:9000
                        |
                        |-- app_network           --> obs-postgres:5432
                        +-- observability_network --> obs-prometheus:9090 (scrapes /metrics)
                                                  --> obs-loki:3100       (receives logs via Promtail)
                                                  --> obs-grafana:3000    (reads Prometheus + Loki)
                                                  --> obs-alertmanager:9093 (receives alerts from Prometheus)

logs_volume --> obs-promtail --> obs-loki --> obs-grafana
obs-node-exporter --> obs-prometheus (host CPU, memory, disk, network)
obs-prometheus --[alert rules]--> obs-alertmanager --[Slack webhook]--> #alerts-*
Django errors --[sentry-sdk]--> sentry.io
```

## Networks

- `app_network` — obs-django, obs-postgres, obs-nginx
- `observability_network` — obs-django, obs-prometheus, obs-alertmanager, obs-loki, obs-promtail, obs-grafana, obs-node-exporter

## Run

```bash
# 1. copy and fill in env
cp django_app/.env.example django_app/.env   # set SLACK_WEBHOOK_URL, SENTRY_DSN, etc.

# 2. start all services
cd django_app
docker compose up --build -d

# 3. check all containers are up
docker compose ps

# 4. view logs
docker compose logs -f obs-django
docker compose logs -f obs-alertmanager
docker compose logs -f obs-prometheus

# 5. stop
docker compose down

# 6. stop + remove volumes (full reset)
docker compose down -v
```

## Verify

```bash
curl http://localhost                           # app via nginx
curl http://localhost/metrics                  # raw prometheus metrics
curl http://localhost:9090                     # prometheus UI (Status → Targets = all UP)
curl http://localhost:9093                     # alertmanager UI
curl http://localhost:3100/ready               # loki ready check
open http://localhost:3000                     # grafana (admin/admin)
```

## Grafana Dashboards

`http://localhost:3000` → Dashboards

| Dashboard | Description |
|-----------|-------------|
| **obs-django Overview** | Request rate, latency p50/p95/p99, status codes, DB queries, memory, logs |
| **obs-postgres Overview** | DB query rate, duration, error rate, query logs |
| **obs-nginx Overview** | Request rate, status breakdown, latency, access logs |
| **obs-prometheus Overview** | All targets status, scrape duration, ingestion rate |
| **obs-loki Overview** | Log ingestion rate, volume by level/app |
| **obs-grafana Overview** | HTTP request rate, response duration, dashboard count |
| **Infrastructure Overview** | Host CPU, memory, disk, network I/O, load average |

## Alerting (Prometheus → Alertmanager → Slack)

Alerts are routed to dedicated Slack channels by category:

| Channel | Alerts |
|---|---|
| `#alerts-http` | `DjangoDown`, `Django5xxError`, `Django4xxError`, `HighHTTP5xxRate`, `HighHTTP4xxRate`, `EndpointHighErrorRate` |
| `#alerts-db` | `DBHighErrorRate`, `DBSlowQueries`, `DBHighQueryRate` |
| `#alerts-latency` | `HighP95Latency`, `HighP99Latency`, `EndpointSlowResponse` |
| `#alerts-infra` | `HighCPUUsage`, `CriticalCPUUsage`, `HighMemoryUsage`, `CriticalMemoryUsage`, `HighDiskUsage`, `DjangoHighMemory` |

### Test alerts via curl

```bash
# Test DjangoDown (stop container, fires in 10s)
docker stop obs-django
docker start obs-django   # sends ✅ RESOLVED

# Test HTTP alert manually
curl -X POST http://localhost:9093/api/v2/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"DjangoDown","severity":"critical","category":"http"},
        "annotations":{"summary":"Django is DOWN","description":"Test alert"}}]'

# Trigger 4xx flood (fires HighHTTP4xxRate after 5 min)
while true; do
  for i in {1..5}; do curl -s -o /dev/null http://localhost/bad-url &; done
  sleep 1
done
```

### Reload Prometheus rules (no restart)

```bash
curl -X POST http://localhost:9090/-/reload
```

## Sentry Error Tracking

Sentry is configured via `sentry-sdk` in Django. Set `SENTRY_DSN` in `.env`.

### Test Sentry from browser

| URL | What it triggers |
|---|---|
| `http://localhost/sentry-debug/` | 🔴 Unhandled `Exception` (500) |
| `http://localhost/sentry-debug/?type=zero` | 🔴 `ZeroDivisionError` (500) |
| `http://localhost/sentry-debug/?type=capture` | 🟡 Manual Sentry message (no 500) |

Check results at [sentry.io](https://sentry.io) → your project → **Issues**.

## .env

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*

# Database
DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=obs-postgres
DB_PORT=5432

# Grafana
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin

# Slack (Alertmanager)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Sentry
SENTRY_DSN=https://<key>@o<org>.ingest.sentry.io/<project>
```

## Troubleshooting

```bash
# Check all Prometheus targets
curl -s "http://localhost:9090/api/v1/targets" | python3 -c "
import json,sys; data=json.load(sys.stdin)
for t in data['data']['activeTargets']:
    print(t['health'], t['labels']['job'], t.get('lastError',''))
"

# Check active alerts in Alertmanager
curl -s http://localhost:9093/api/v2/alerts | python3 -m json.tool

# Check alertmanager logs (crash / config errors)
docker compose logs obs-alertmanager --tail=30

# Check loki receiving logs
curl -s "http://localhost:3100/loki/api/v1/labels"

# Check promtail shipping logs
docker compose logs obs-promtail --tail=10
```

## Phase Progress

- [x] Django + uv
- [x] PostgreSQL (Docker)
- [x] Nginx
- [x] Prometheus + /metrics
- [x] Loki + Promtail
- [x] Grafana dashboards (7 dashboards)
- [x] Node Exporter (host metrics)
- [x] Alertmanager + Slack notifications
- [x] Sentry error tracking
