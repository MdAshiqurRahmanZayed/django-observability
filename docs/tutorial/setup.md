# Step 1: Setup Your Environment

<div align="center" markdown>

**Let's get your development environment ready!**

</div>

---

## 📋 What You'll Learn

In this step, you'll:

- Install Docker Desktop
- Clone the repository
- Configure environment variables
- Start the observability stack

---

## 🛠️ Prerequisites Check

Before starting, verify you have these installed:

=== "Mac"

    ```bash
    # Check Docker
    docker --version
    # Should show: Docker version 20.10+
    
    # Check Docker Compose
    docker compose version
    # Should show: Docker Compose version 2.0+
    
    # Check Git
    git --version
    # Should show: git version 2.0+
    ```

=== "Windows"

    ```powershell
    # Check Docker (in PowerShell or WSL)
    docker --version
    
    # Check Docker Compose
    docker compose version
    
    # Check Git
    git --version
    ```

=== "Linux"

    ```bash
    # Check Docker
    docker --version
    
    # Check Docker Compose
    docker compose version
    
    # Check Git
    git --version
    ```

??? tip "Don't have Docker?"
    
    Download and install Docker Desktop:
    
    - [Mac](https://desktop.docker.com/mac/main/arm64/Docker.dmg)
    - [Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
    - [Linux](https://docs.docker.com/engine/install/)
    
    After installation, start Docker Desktop and wait for it to be ready.

---

## 📥 Clone the Repository

```bash
# Clone the repository
git clone https://github.com/MdAshiqurRahmanZayed/django-observability.git

# Navigate to the project
cd django-observability
```

---

## ⚙️ Configure Environment

### Step 1: Create Environment File

```bash
cp django_app/.env.example django_app/.env
```

### Step 2: Understand the Configuration

Open `django_app/.env` and review the settings:

```bash
# ┌──────────────────────────────────────────────┐
# │          DATABASE CONFIGURATION              │
# └──────────────────────────────────────────────┘
DB_NAME=todo_db          # Database name
DB_USER=postgres         # Database username
DB_PASSWORD=postgres     # Database password
DB_HOST=obs-postgres     # Docker internal hostname
DB_PORT=5432             # Database port

# ┌──────────────────────────────────────────────┐
# │          GRAFANA CONFIGURATION               │
# └──────────────────────────────────────────────┘
GF_ADMIN_USER=admin      # Grafana admin username
GF_ADMIN_PASSWORD=admin  # Grafana admin password

# ┌──────────────────────────────────────────────┐
# │          SLACK ALERTS (Optional)             │
# └──────────────────────────────────────────────┘
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

??? info "What each setting does"
    
    | Setting | Purpose | Default |
    |---------|---------|---------|
    | `DB_NAME` | PostgreSQL database name | todo_db |
    | `DB_USER` | Database login username | postgres |
    | `DB_PASSWORD` | Database login password | postgres |
    | `DB_HOST` | Database hostname (Docker internal) | obs-postgres |
    | `DB_PORT` | Database port | 5432 |
    | `GF_ADMIN_USER` | Grafana admin username | admin |
    | `GF_ADMIN_PASSWORD` | Grafana admin password | admin |
    | `SLACK_WEBHOOK_URL` | Slack webhook for alerts | (optional) |

---

## 🚀 Start the Stack

### Start All Services

```bash
docker compose -f django_app/docker-compose.yml up -d
```

This command:

1. Pulls all required Docker images
2. Creates Docker networks
3. Starts all 10 containers
4. Configures volumes for persistent data

### Wait for Services

The first startup may take 1-2 minutes to download images.

```bash
# Watch the startup progress
docker compose -f django_app/docker-compose.yml logs -f
```

Press `Ctrl+C` to stop watching logs.

---

## ✅ Verify Installation

### Check Container Status

```bash
docker compose -f django_app/docker-compose.yml ps
```

You should see all containers with `Up` status:

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

### Quick Health Checks

```bash
# Test Django
curl -f http://localhost/ || echo "Django not ready"

# Test Prometheus
curl -f http://localhost:9090/-/healthy || echo "Prometheus not ready"

# Test Grafana
curl -f http://localhost:3000/api/health || echo "Grafana not ready"
```

---

## 🌐 Access Your Services

Open these URLs in your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| 🌐 **Django App** | http://localhost | - |
| 📊 **Grafana** | http://localhost:3000 | admin / admin |
| 📈 **Prometheus** | http://localhost:9090 | - |
| 🔔 **Alertmanager** | http://localhost:9093 | - |
| 🗄️ **pgAdmin** | http://localhost:5050 | admin@admin.com / admin |

---

## 🎉 Setup Complete!

Your observability stack is now running! 

### What's Next?

In the next step, you'll learn how to:

- View Django metrics in Prometheus
- Create Grafana dashboards
- Query logs in Loki

---

<div align="center" markdown>

**Ready for Step 2?** 👇

[Step 2: Metrics →](metrics.md){ .md-button .md-button--primary }

</div>
