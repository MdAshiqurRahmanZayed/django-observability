# Django Observability

## Stack & Ports

| Service       | Container         | Port          | Purpose                |
|---------------|-------------------|---------------|------------------------|
| Django        | obs-django        | internal 9000 | App (no direct access) |
| Nginx         | obs-nginx         | 80            | Entry point            |
| PostgreSQL    | obs-postgres      | internal 5432 | Database               |
| Prometheus    | obs-prometheus    | 9090          | Metrics scraper        |
| Loki          | obs-loki          | 3100          | Log storage            |
| Promtail      | obs-promtail      | internal      | Log shipper            |
| Grafana       | obs-grafana       | 3000          | Dashboards             |
| Node Exporter | obs-node-exporter | internal 9100 | Host metrics           |

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
                                                  --> obs-loki:3100       (receives logs)
                                                  --> obs-grafana:3000    (reads prometheus + loki)

logs_volume --> obs-promtail --> obs-loki --> obs-grafana

obs-node-exporter --> obs-prometheus (host CPU, memory, disk, network)
```

## Networks

- `app_network` — obs-django, obs-postgres, obs-nginx
- `observability_network` — obs-django, obs-prometheus, obs-loki, obs-promtail, obs-grafana, obs-node-exporter

## Run

```bash
# 1. install dependencies
cd django_app
uv sync
cd ..

# 2. start all services
cd django_app
docker compose up --build -d

# 3. check all containers
docker compose ps

# 4. view logs
docker compose logs -f
docker compose logs -f obs-django
docker compose logs -f obs-prometheus
docker compose logs -f obs-grafana
docker compose logs -f obs-promtail

# 5. stop
docker compose down

# 6. stop + remove volumes (full reset)
docker compose down -v
```

## Verify

```bash
curl http://localhost                     # app via nginx
curl http://localhost/metrics             # raw prometheus metrics
curl http://localhost:9090                # prometheus UI (Status -> Targets = all UP)
curl http://localhost:3100/ready          # loki ready check
curl http://localhost:3100/loki/api/v1/labels  # loki labels (should show app, level, etc)
open http://localhost:3000                # grafana (admin/admin)
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

## Generate Test Data

```bash
# generate traffic + logs
for i in {1..20}; do curl -s http://localhost/ > /dev/null; done
curl http://localhost/api/todos/     # API call
curl http://localhost/nonexistent    # 404 error log
```

## .env

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,obs-django

# Database
DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=obs-postgres
DB_PORT=5432

# Grafana
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin
```

## Troubleshooting

```bash
# check all targets up
curl -s "http://localhost:9090/api/v1/targets" | python3 -c "
import json,sys; data=json.load(sys.stdin)
for t in data['data']['activeTargets']:
    print(t['health'], t['labels']['job'], t.get('lastError',''))
"

# check loki receiving logs
curl -s "http://localhost:3100/loki/api/v1/labels"

# check promtail shipping logs
docker logs obs-promtail 2>&1 | tail -10

# reload prometheus config without restart
curl -X POST http://localhost:9090/-/reload
```

## Phase Progress

- [x] Django + uv
- [x] PostgreSQL (Docker)
- [x] Nginx
- [x] Prometheus + /metrics
- [x] Loki + Promtail
- [x] Grafana dashboards (7 dashboards)
- [x] Node Exporter (host metrics)
- [ ] Alertmanager
- [ ] Sentry
