# Django Observability

## Stack & Ports

| Service    | Container    | Port          | Purpose                |
|------------|--------------|---------------|------------------------|
| Django     | django-app   | internal 9000 | App (no direct access) |
| Nginx      | nginx        | 80            | Entry point            |
| PostgreSQL | postgres-db  | internal 5432 | Database               |
| Prometheus | prometheus   | 9090          | Metrics scraper        |
| Loki       | loki         | 3100          | Log storage            |
| Promtail   | promtail     | internal      | Log shipper            |
| Grafana    | grafana      | 3000          | Dashboards             |

## Architecture

```
Browser
   |
   v
Nginx :80
   |
   |---> /static  -> staticfiles volume
   |---> /media   -> mediafiles volume
   +---> /        -> django-app:9000
                        |
                        |-- app_network           --> postgres-db:5432
                        +-- observability_network --> prometheus:9090 (scrapes /metrics)
                                                  --> loki:3100      (receives logs)
                                                  --> grafana:3000   (reads prometheus + loki)

logs_volume --> promtail --> loki --> grafana
```

## Networks

- `app_network` — django, postgres, nginx
- `observability_network` — django, prometheus, loki, promtail, grafana

## Run

```bash
# 1. install dependencies
cd django_app
uv sync
cd ..

# 2. start all services
docker compose up --build -d

# 3. check all containers
docker compose ps

# 4. view logs
docker compose logs -f
docker compose logs -f django
docker compose logs -f prometheus
docker compose logs -f grafana
docker compose logs -f promtail

# 5. stop
docker compose down

# 6. stop + remove volumes (full reset)
docker compose down -v
```

## Verify

```
http://localhost           -> app via nginx
http://localhost/metrics   -> raw prometheus metrics
http://localhost:9090      -> prometheus UI  (Status -> Targets = UP)
http://localhost:3100/ready -> loki ready check
http://localhost:3000      -> grafana (admin/admin)
```

## Grafana Dashboard

`http://localhost:3000` → Dashboards → Django → **Django Project Overview**

| Panel | Source |
|-------|--------|
| Container status | Prometheus |
| Request rate | Prometheus |
| Response time p50/p95/p99 | Prometheus |
| HTTP status codes | Prometheus |
| DB query rate + duration | Prometheus |
| Django memory usage | Prometheus |
| Live log stream | Loki |
| DB query logs | Loki |
| Error logs | Loki |
| Gunicorn access logs | Loki |

## Generate Test Data

```bash
# generate traffic + logs
for i in {1..20}; do curl -s http://localhost/ > /dev/null; done
curl http://localhost/nonexistent   # 404 error log
```

## .env

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres-db
DB_PORT=5432

GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin
```

## Phase Progress

- [x] Django + uv
- [x] PostgreSQL (Docker)
- [x] Nginx
- [x] Prometheus + /metrics
- [x] Loki + Promtail
- [x] Grafana dashboards
- [ ] Node Exporter + cAdvisor
- [ ] Alertmanager
- [ ] Tracing (OpenTelemetry + Tempo + Jaeger)
- [ ] Sentry
