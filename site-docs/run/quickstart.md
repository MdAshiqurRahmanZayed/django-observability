# Quick Start

Run the entire Django Observability Stack in **3 commands**.

---

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |
| Git | 2.0+ | `git --version` |

---

## 3-Step Setup

### Step 1: Clone & Navigate

```bash
git clone https://github.com/MdAshiqurRahmanZayed/django-observability.git
cd django-observability
```

### Step 2: Configure Environment

```bash
cp django_app/.env.example django_app/.env
```

### Step 3: Start Everything

```bash
docker compose -f django_app/docker-compose.yml up -d
```

???+ success "Expected Output"
    ```
    [+] Running 11/11
     ✔ Container obs-postgres         Started
     ✔ Container obs-loki             Started
     ✔ Container obs-node-exporter    Started
     ✔ Container obs-prometheus       Started
     ✔ Container obs-alertmanager     Started
     ✔ Container obs-grafana          Started
     ✔ Container obs-promtail         Started
     ✔ Container obs-nginx            Started
     ✔ Container obs-pgadmin          Started
     ✔ Container obs-django           Started
    ```

---

## Verify

```bash
docker compose -f django_app/docker-compose.yml ps
```

---

## Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Django App | http://localhost | - |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Alertmanager | http://localhost:9093 | - |
| pgAdmin | http://localhost:5050 | admin@admin.com / admin |

---

## Stop Everything

```bash
docker compose -f django_app/docker-compose.yml down
```

---

## Next Steps

- [Docker Commands](docker.md) - All Docker operations
- [Individual Services](django.md) - Run services separately
