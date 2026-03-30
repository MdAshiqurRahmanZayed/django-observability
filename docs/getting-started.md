# Getting Started

<div align="center" markdown>

**🎉 Welcome! Let's get your observability stack running in 5 minutes.**

</div>

---

## 📋 Prerequisites

Before you begin, make sure you have:

| Requirement | Version | Download |
|-------------|---------|----------|
| Docker Desktop | 20.10+ | [Download](https://www.docker.com/products/docker-desktop/) |
| Git | 2.0+ | [Download](https://git-scm.com/) |
| Terminal | Any | Built-in on Mac/Linux |

??? tip "Docker Desktop Tips"

    - **Mac**: Docker Desktop for Mac
    - **Windows**: Docker Desktop for Windows (enable WSL2)
    - **Linux**: Install via your package manager

    Make sure Docker is running before proceeding!

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/MdAshiqurRahmanZayed/django-observability.git
cd django-observability
```

### Step 2: Configure Environment

```bash
cp django_app/.env.example django_app/.env
```

The `.env` file contains all configuration. Here's what each setting does:

```bash
# Database Configuration
DB_NAME=todo_db          # Your database name
DB_USER=postgres         # Database username
DB_PASSWORD=postgres     # Database password (change this in production!)
DB_HOST=obs-postgres     # Internal Docker hostname
DB_PORT=5432             # Database port

# Grafana Configuration
GF_ADMIN_USER=admin      # Grafana admin username
GF_ADMIN_PASSWORD=admin  # Grafana admin password (change this!)

# Slack Alerts (optional - leave empty to disable)
SLACK_WEBHOOK_URL=

# Sentry (optional - leave empty to disable)
SENTRY_DSN=
```

??? info "How to get Slack Webhook URL"

    1. Go to https://api.slack.com/apps
    2. Click **Create New App** → **From scratch**
    3. Name it (e.g., "Django Alerts") and select workspace
    4. Go to **Incoming Webhooks** → Toggle **On**
    5. Click **Add New Webhook to Workspace**
    6. Select channel (e.g., #alerts)
    7. Copy the webhook URL

    **Format:** `See https://api.slack.com/apps to get your webhook URL`

??? info "How to get Sentry DSN"

    1. Go to https://sentry.io (create account if needed)
    2. Click **Create Project** → Select **Django**
    3. Copy the DSN from the setup page
    4. Or go to **Settings** → **Projects** → **Your Project** → **Client Keys (DSN)**

    **Format:** `https://<key>@o<org>.ingest.sentry.io/<project>`

!!! warning "Leave empty to disable"

    If you don't need Slack alerts or Sentry error tracking, leave these values empty. Invalid values will cause errors.

### Step 3: Start All Services

```bash
docker compose -f django_app/docker-compose.yml up -d --build
```

This starts **10 containers**:

| Container | Purpose |
|-----------|---------|
| obs-django | Django application |
| obs-postgres | PostgreSQL database |
| obs-prometheus | Metrics collection |
| obs-grafana | Visualization |
| obs-loki | Log aggregation |
| obs-promtail | Log shipping |
| obs-alertmanager | Alert routing |
| obs-nginx | Reverse proxy |
| obs-node-exporter | System metrics |
| obs-pgadmin | Database admin |

### Step 4: Verify Everything is Running

```bash
docker compose -f django_app/docker-compose.yml ps
```

Expected output:

```
NAME                 STATUS          PORTS
obs-django           Up              0.0.0.0:9000->9000/tcp
obs-postgres         Up              0.0.0.0:5439->5432/tcp
obs-prometheus       Up              0.0.0.0:9090->9090/tcp
obs-grafana          Up              0.0.0.0:3000->3000/tcp
obs-loki             Up              0.0.0.0:3100->3100/tcp
obs-promtail         Up              -
obs-alertmanager     Up              0.0.0.0:9093->9093/tcp
obs-nginx            Up              0.0.0.0:80->80/tcp
obs-node-exporter    Up              0.0.0.0:9100->9100/tcp
obs-pgadmin          Up              0.0.0.0:5050->80/tcp
```

---

## 🌐 Access Your Stack

Open these URLs in your browser:

| Service | URL | Credentials | What You'll See |
|---------|-----|-------------|-----------------|
| 🌐 **Django App** | <http://localhost> | - | Todo application |
| 📊 **Grafana** | <http://localhost:3000> | admin / admin | Dashboards & graphs |
| 📈 **Prometheus** | <http://localhost:9090> | - | Metrics & queries |
| 🔔 **Alertmanager** | <http://localhost:9093> | - | Alert status |
| 🗄️ **pgAdmin** | <http://localhost:5050> | <admin@admin.com> / admin | Database admin |

---

## ✅ Verify Your Setup

### Test 1: Django Application

```bash
curl http://localhost/
```

You should see HTML response from the Django app.

### Test 2: Metrics Endpoint

```bash
curl http://localhost:9000/metrics | head
```

You should see Prometheus metrics like:

```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 1234.0
```

### Test 3: Prometheus Health

```bash
curl http://localhost:9090/-/healthy
```

Expected: `Prometheus Server is Healthy.`

### Test 4: Grafana Health

```bash
curl http://localhost:3000/api/health
```

Expected: `{"database":"ok"}`

---

## 🎉 What's Next?

Now that your stack is running, explore these tutorials:

### Beginner Path

1. [Architecture Overview](architecture.md) - Understand how everything connects
2. [Django App Module](modules/01-django-app.md) - See how metrics are collected
3. [Grafana Module](modules/03-grafana.md) - Create your first dashboard

### Intermediate Path

1. [Prometheus Module](modules/02-prometheus.md) - Learn PromQL queries
2. [Loki Module](modules/04-loki.md) - Search logs with LogQL
3. [Alertmanager Module](modules/06-alertmanager.md) - Set up Slack alerts

### Advanced Path

1. [MCP Server Module](modules/08-mcp-server.md) - AI integration
2. [Custom Dashboards](modules/03-grafana.md#creating-dashboards) - Build your own
3. [Custom Alerts](modules/06-alertmanager.md) - Create custom alert rules

---

## 🔧 Common Commands

```bash
# Start all services
docker compose -f django_app/docker-compose.yml up -d

# Stop all services
docker compose -f django_app/docker-compose.yml down

# Restart a specific service
docker compose -f django_app/docker-compose.yml restart obs-django

# View logs for a service
docker logs -f obs-django

# Access container shell
docker exec -it obs-django /bin/sh

# Rebuild and restart (after code changes)
docker compose -f django_app/docker-compose.yml up -d --build obs-django
```

---

## ❓ Troubleshooting

??? failure "Docker not running"

    Make sure Docker Desktop is running:

    ```bash
    docker ps
    ```

    If you get an error, start Docker Desktop and try again.

??? failure "Port already in use"

    If you get "port is already allocated" error:

    ```bash
    # Find what's using the port
    lsof -i :3000

    # Stop the conflicting service or change the port in docker-compose.yml
    ```

??? failure "Services not starting"

    Check logs for errors:

    ```bash
    docker compose -f django_app/docker-compose.yml logs
    ```

    Common issues:
    - Database not ready (wait a few seconds)
    - Environment variables not set (check `.env`)
    - Docker resources insufficient (increase memory in Docker Desktop)

??? failure "Cannot connect to localhost"

    Try these URLs instead:

    - http://127.0.0.1:3000 (Grafana)
    - http://0.0.0.0:3000 (Grafana)

    Or check if containers are running:

    ```bash
    docker ps
    ```

---

## 📚 More Resources

- [Architecture Overview](architecture.md)
- [Module Documentation](modules/01-django-app.md)
- [API Reference](reference/api.md)
- [Troubleshooting Guide](reference/troubleshooting.md)

---

<div align="center" markdown>

**Ready to learn more?** 👇

[Architecture Overview →](architecture.md){ .md-button .md-button--primary }

</div>
