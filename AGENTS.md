# AGENTS.md

This file provides instructions for AI assistants working on this project.

---

## Project Overview

Django Observability Stack - A complete observability solution for Django applications with Prometheus, Grafana, Loki, and AI integration.

---

## Project Structure

```
django-observability/
├── django_app/                 # Django application
│   ├── config/                 # Django settings, URLs
│   ├── todo/                   # Todo app (example)
│   ├── docker-compose.yml      # All services configuration
│   ├── Dockerfile              # Django Docker image
│   ├── .env.example            # Environment template
│   └── requirements.txt        # Python dependencies
├── prometheus/                 # Prometheus configuration
│   ├── prometheus.yml          # Scrape configuration
│   └── rules/                  # Alert rules
├── loki/                       # Loki configuration
│   └── loki-config.yml         # Loki settings
├── promtail/                   # Promtail configuration
│   └── promtail-config.yml     # Log shipping config
├── alertmanager/               # Alertmanager configuration
│   └── alertmanager.yml        # Alert routing config
├── grafana/                    # Grafana configuration
│   └── provisioning/           # Datasources, dashboards
├── nginx/                      # Nginx configuration
│   └── nginx.conf              # Reverse proxy config
├── docs/                       # MkDocs documentation
│   ├── index.md                # Home page
│   ├── getting-started.md      # Setup guide
│   ├── modules/                # Module documentation
│   └── tutorial/               # Step-by-step tutorials
├── screenshots/                # Documentation images
├── mkdocs.yml                  # MkDocs configuration
├── .github/                    # GitHub Actions
│   └── workflows/              # CI/CD workflows
└── AGENTS.md                   # This file
```

---

## Commands

### Docker

```bash
# Start all services
docker compose -f django_app/docker-compose.yml up -d --build

# Stop all services
docker compose -f django_app/docker-compose.yml down

# Restart specific service
docker compose -f django_app/docker-compose.yml restart obs-django

# View logs
docker logs -f obs-django

# Access shell
docker exec -it obs-django /bin/sh
```

### Documentation

```bash
# Build documentation
mkdocs build

# Serve locally
mkdocs serve
```

### Pre-commit

```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run markdownlint --files docs/*.md
```

---

## Conventions

### Docker

- Use `obs-` prefix for container names
- Use `observability_network` for monitoring services
- Use `app_network` for application services
- Mount config files as read-only (`:ro`)

### Documentation

- Use MkDocs Material theme
- Add section headers with `#` comments
- Add detailed comments to all YAML files
- Link to actual config files on GitHub

### YAML Configuration

- Add section headers with `# ====` comments
- Add inline comments explaining each setting
- Use 2-space indentation
- Keep lines under 120 characters

### Git

- Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Create branches from `main`
- Test before committing

---

## Configuration Files

| File | Purpose | Format |
|------|---------|--------|
| `prometheus/prometheus.yml` | Metrics collection | YAML |
| `loki/loki-config.yml` | Log storage | YAML |
| `promtail/promtail-config.yml` | Log shipping | YAML |
| `alertmanager/alertmanager.yml` | Alert routing | YAML |
| `grafana/provisioning/datasources/datasources.yml` | Grafana datasources | YAML |
| `mkdocs.yml` | Documentation config | YAML |
| `django_app/.env` | Environment variables | Shell |

---

## Services

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Django | 9000 | http://localhost:9000 | Application |
| Prometheus | 9090 | http://localhost:9090 | Metrics |
| Loki | 3100 | http://localhost:3100 | Logs |
| Alertmanager | 9093 | http://localhost:9093 | Alerts |
| Grafana | 3000 | http://localhost:3000 | Dashboards |
| Node Exporter | 9100 | http://localhost:9100 | Host metrics |
| pgAdmin | 5050 | http://localhost:5050 | DB admin |
| Nginx | 80 | http://localhost:80 | Reverse proxy |

---

## Data Flow

```
Django → GET /metrics → Prometheus → Alertmanager → Slack
Django → Log File → Promtail → POST /loki/api/v1/push → Loki
Prometheus + Loki → Grafana (Dashboards)
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_NAME | todo_db | Database name |
| DB_USER | postgres | Database username |
| DB_PASSWORD | postgres | Database password |
| DB_HOST | obs-postgres | Database host |
| DB_PORT | 5432 | Database port |
| GF_ADMIN_USER | admin | Grafana username |
| GF_ADMIN_PASSWORD | admin | Grafana password |
| SLACK_WEBHOOK_URL | (empty) | Slack webhook |
| SENTRY_DSN | (empty) | Sentry DSN |

---

## Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose -f django_app/docker-compose.yml logs

# Check health
docker ps

# Restart all
docker compose -f django_app/docker-compose.yml restart
```

### Port Conflicts

```bash
# Find process using port
lsof -i :3000

# Kill process
kill $(lsof -t -i :3000)
```

### Network Issues

```bash
# Check networks
docker network ls

# Inspect network
docker network inspect django_app_observability_network
```

---

## Testing

### Pre-commit

```bash
pre-commit run --all-files
```

### Documentation

```bash
mkdocs build --strict
```

### Docker

```bash
docker compose -f django_app/docker-compose.yml config
```

---

## Links

- GitHub: https://github.com/MdAshiqurRahmanZayed/django-observability
- Documentation: https://mdashiqurrahmanzayed.github.io/django-observability/
- Issues: https://github.com/MdAshiqurRahmanZayed/django-observability/issues
