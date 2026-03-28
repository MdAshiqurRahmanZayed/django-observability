# Django Observability

A full-stack Django observability setup with metrics, logs, alerting, and AI integration.

![Django](https://img.shields.io/badge/Django-5.x-green)
![Prometheus](https://img.shields.io/badge/Prometheus-Latest-blue)
![Grafana](https://img.shields.io/badge/Grafana-Latest-orange)
![Loki](https://img.shields.io/badge/Loki-2.9.0-purple)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

---

## Quick Start

```bash
# Clone
git clone https://github.com/MdAshiqurRahmanZayed/django-observability.git
cd django-observability

# Configure
cp django_app/.env.example django_app/.env

# Run
docker compose -f django_app/docker-compose.yml up -d
```

---

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| Django | http://localhost | Application |
| Grafana | http://localhost:3000 | Dashboards |
| Prometheus | http://localhost:9090 | Metrics |
| Alertmanager | http://localhost:9093 | Alerts |
| Loki | http://localhost:3100 | Logs |
| pgAdmin | http://localhost:5050 | Database Admin |

---

## Architecture

```
Browser → Nginx → Django → PostgreSQL
              ↓
         Prometheus → Alertmanager → Slack
              ↓
         Grafana ← Loki ← Promtail
```

---

## Documentation

📚 **Full documentation:** [GitHub Pages](https://mdashiqurrahmanzayed.github.io/django-observability/)

- [Getting Started](https://mdashiqurrahmanzayed.github.io/django-observability/getting-started/)
- [Architecture](https://mdashiqurrahmanzayed.github.io/django-observability/architecture/)
- [Tutorial](https://mdashiqurrahmanzayed.github.io/django-observability/tutorial/setup/)
- [Modules](https://mdashiqurrahmanzayed.github.io/django-observability/modules/01-django-app/)
- [Contributing](https://mdashiqurrahmanzayed.github.io/django-observability/contributing/)

---

## Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d

# Stop
docker compose -f django_app/docker-compose.yml down

# Logs
docker logs -f obs-django

# Restart
docker compose -f django_app/docker-compose.yml restart obs-django
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT
