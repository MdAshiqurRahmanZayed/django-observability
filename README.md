# Django Observability

## Stack & Ports

| Service    | Container    | Port          | Purpose                |
|------------|--------------|---------------|------------------------|
| Django     | django-app   | internal 9000 | App (no direct access) |
| Nginx      | nginx        | 80            | Entry point            |
| PostgreSQL | postgres-db  | internal 5432 | Database               |
| Prometheus | prometheus   | 9090          | Metrics scraper        |

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
                        +-- observability_network --> prometheus:9090
                                                       scrapes /metrics
```

## Networks

- `app_network` — django, postgres, nginx
- `observability_network` — django, prometheus

## Run

```bash
cd django_app
uv sync
cd ..

docker compose up --build -d

docker compose ps

docker compose logs -f
docker compose logs -f django
docker compose logs -f prometheus


docker compose down

docker compose down -v
```

## Verify

```
http://localhost          -> app via nginx
http://localhost/metrics  -> raw prometheus metrics
http://localhost:9090     -> prometheus UI (Status -> Targets = UP)
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
```

## Phase Progress

- [x] Django + uv
- [x] PostgreSQL (Docker)
- [x] Nginx
- [x] Prometheus + /metrics
- [ ] Loki + Promtail
- [ ] Grafana
- [ ] Node Exporter + cAdvisor
- [ ] Alertmanager
- [ ] Tracing (OpenTelemetry + Tempo + Jaeger)
- [ ] Sentry
