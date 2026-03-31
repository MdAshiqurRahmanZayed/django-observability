# PostgreSQL

## Overview

PostgreSQL is the primary relational database for the Django application, storing all application data including user information, todo items, and other models. It provides ACID-compliant transactions, robust data integrity, and excellent performance for web applications.

## Description

PostgreSQL is a powerful, open-source object-relational database system with over 35 years of active development. In this stack, it:

- Stores Django application data (models, users, sessions)
- Provides ACID-compliant transactions
- Supports JSON/JSONB for flexible data storage
- Offers full-text search capabilities
- Handles concurrent connections efficiently

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        POSTGRESQL IN STACK                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   APPLICATION LAYER                                                         │
│   ─────────────────                                                         │
│   ┌─────────────┐     SQL Queries     ┌─────────────────────┐               │
│   │   Django    │ ◀──────────────────▶│    PostgreSQL       │               │
│   │   :9000     │   psycopg2 driver   │       :5432         │               │
│   └─────────────┘                     └─────────┬─────────-─┘               │
│                                                 │                           │
│   MANAGEMENT (Optional)                         │                           │
│   ─────────────────────                         │                           │
│                                                 ▼                           │
│   ┌─────────────┐     Admin UI        ┌─────────────────────┐               │
│   │  pgAdmin    │ ◀──────────────────▶│    PostgreSQL       │               │
│   │   :5050     │   Port 5432         │       :5432         │               │
│   └─────────────┘                     └─────────────────────┘               │
│                                                                             │
│   DATA PERSISTENCE                                                          │
│   ────────────────                                                          │
│   ┌─────────────────────────────────────────────────────────┐               │
│   │              postgres_data Volume                       │               │
│   │         /var/lib/postgresql/data                        │               │
│   └─────────────────────────────────────────────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Database | PostgreSQL | 16 (Alpine) |
| Driver | psycopg2 | 2.9.x |
| Management | pgAdmin | 4 (latest) |

## Docker Configuration

### docker-compose.yml

```yaml
# PostgreSQL Database
obs-postgres:
  image: postgres:16-alpine             # PostgreSQL 16 on Alpine (smaller image)
  container_name: obs-postgres
  restart: unless-stopped
  ports:
    - "5439:5432"                       # Expose on host port 5439
  environment:
    POSTGRES_DB:       ${DB_NAME}       # Database name
    POSTGRES_USER:     ${DB_USER}       # Database username
    POSTGRES_PASSWORD: ${DB_PASSWORD}   # Database password
  volumes:
    - postgres_data:/var/lib/postgresql/data  # Persistent database storage
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
    interval: 10s                       # Check every 10 seconds
    timeout: 5s                         # Wait 5 seconds for response
    retries: 5                          # Try 5 times before failing
    start_period: 10s                   # Wait 10s before first check
  networks:
    - app_network                       # Django can connect here
```

### pgAdmin Service

```yaml
# pgAdmin Web Interface
obs-pgadmin:
  image: dpage/pgadmin4:latest          # pgAdmin on Alpine
  container_name: obs-pgadmin
  restart: unless-stopped
  ports:
    - "5050:80"                         # pgAdmin UI port
  env_file:
    - .env                              # Load environment variables
  environment:
    PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL:-admin@admin.com}
    PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD:-admin}
  volumes:
    - pgadmin_data:/var/lib/pgadmin     # pgAdmin configuration storage
  depends_on:
    - obs-postgres                      # PostgreSQL must be ready
  networks:
    - app_network                       # Can connect to PostgreSQL
```

## Network Access

| Access | URL | Purpose |
|--------|-----|---------|
| External | `localhost:5439` | Direct database access (development) |
| Internal (Docker) | `obs-postgres:5432` | Application connection |
| pgAdmin | `http://localhost:5050` | Database management UI |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_NAME` | `todo_db` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `postgres` | Database password |
| `DB_HOST` | `obs-postgres` | Database host (Docker) |
| `DB_PORT` | `5432` | Database port |
| `PGADMIN_DEFAULT_EMAIL` | `admin@admin.com` | pgAdmin login email |
| `PGADMIN_DEFAULT_PASSWORD` | `admin` | pgAdmin login password |

## Django Configuration

### settings.py

```python
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432", cast=int),
    }
}
```

### Connection Details

- **Engine**: `django_prometheus.db.backends.postgresql` (includes query metrics)
- **Host**: `obs-postgres` (Docker service name)
- **Port**: `5432` (internal), `5439` (external mapping)
- **Driver**: `psycopg2-binary`

## How It Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      POSTGRESQL WORKING PROCESS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. STARTUP                                                                │
│   ───────────                                                               │
│   PostgreSQL container starts                                               │
│   Reads environment variables (DB_NAME, DB_USER, DB_PASSWORD)               │
│   Initializes database if first run                                         │
│   Starts listening on port 5432                                             │
│                                                                             │
│   2. HEALTH CHECK                                                           │
│   ──────────────                                                            │
│   Docker runs pg_isready every 10 seconds                                   │
│   Checks if database is accepting connections                               │
│   Django waits for health check before starting                             │
│                                                                             │
│   3. CONNECTION                                                             │
│   ───────────                                                               │
│   Django connects via psycopg2 driver                                       │
│   Connection pool managed by Django ORM                                     │
│   Queries executed via SQL                                                  │
│                                                                             │
│   4. DATA STORAGE                                                           │
│   ──────────────                                                            │
│   Data persisted to postgres_data volume                                    │
│   Write-Ahead Logging (WAL) for durability                                  │
│   Automatic checkpoints and vacuum                                          │
│                                                                             │
│   5. MONITORING                                                             │
│   ───────────                                                               │
│   Prometheus scrapes query metrics via django-prometheus                    │
│   Slow queries logged for analysis                                          │
│   Connection stats available via pg_stat                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Useful Commands

### Container Management

```bash
# Start PostgreSQL
docker compose -f django_app/docker-compose.yml up -d obs-postgres

# Stop PostgreSQL
docker compose -f django_app/docker-compose.yml stop obs-postgres

# View logs
docker logs -f obs-postgres

# Access shell
docker exec -it obs-postgres /bin/sh
```

### Database Operations

```bash
# Connect to database
docker exec -it obs-postgres psql -U postgres -d todo_db

# List databases
docker exec -it obs-postgres psql -U postgres -c "\l"

# List tables
docker exec -it obs-postgres psql -U postgres -d todo_db -c "\dt"

# Check database size
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT pg_size_pretty(pg_database_size('todo_db'));"
```

### Health Checks

```bash
# Check if PostgreSQL is ready
docker exec obs-postgres pg_isready -U postgres -d todo_db

# Expected output:
# /var/run/postgresql:5432 - accepting connections

# Check via Docker health
docker ps --filter "name=obs-postgres" --format "{{.Status}}"
```

### Backup & Restore

```bash
# Backup database
docker exec -t obs-postgres pg_dump -U postgres todo_db > backup.sql

# Restore database
docker exec -i obs-postgres psql -U postgres todo_db < backup.sql

# Backup with compression
docker exec -t obs-postgres pg_dump -U postgres todo_db | gzip > backup.sql.gz

# Restore compressed backup
gunzip -c backup.sql.gz | docker exec -i obs-postgres psql -U postgres todo_db
```

### Performance Analysis

```bash
# Check active connections
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT * FROM pg_stat_activity;"

# Check table sizes
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;"

# Check slow queries (if logging enabled)
docker logs obs-postgres | grep "duration:"
```

## pgAdmin Usage

### Access pgAdmin

1. Open browser to `http://localhost:5050`
2. Login with credentials from `.env`:
   - Email: `admin@admin.com`
   - Password: `admin`

### Add Server Connection

1. Right-click "Servers" → Register → Server
2. General tab:
   - Name: `obs-postgres`
3. Connection tab:
   - Host: `obs-postgres` (Docker service name)
   - Port: `5432`
   - Maintenance database: `todo_db`
   - Username: `postgres`
   - Password: `postgres`

### Common pgAdmin Tasks

| Task | Location |
|------|----------|
| View tables | Servers → obs-postgres → Databases → todo_db → Schemas → public → Tables |
| Run query | Tools → Query Tool |
| View data | Right-click table → View/Edit Data |
| Backup | Right-click database → Backup |
| Restore | Right-click database → Restore |

## Data Persistence

### Volume Configuration

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

- **Volume**: `postgres_data`
- **Mount Point**: `/var/lib/postgresql/data`
- **Purpose**: Persists database files across container restarts
- **Lifetime**: Survives `docker compose down` (only removed with `-v` flag)

### Backup Volume Data

```bash
# Backup volume to tar
docker run --rm -v django-observability_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volume from tar
docker run --rm -v django-observability_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Django | `obs-postgres:5432` | Application data storage |
| pgAdmin | `obs-postgres:5432` | Database management |
| Prometheus | Via django-prometheus | Query metrics |

## Monitoring with Prometheus

The `django-prometheus` backend provides automatic query metrics:

| Metric | Description |
|--------|-------------|
| `django_db_query_duration_seconds` | Query execution time |
| `django_db_query_total` | Total query count |
| `django_db_query_errors_total` | Failed query count |

### Sample PromQL Queries

```promql
# Database query rate
rate(django_db_query_total[5m])

# Average query duration
rate(django_db_query_duration_seconds_sum[5m]) / rate(django_db_query_duration_seconds_count[5m])

# Error rate
rate(django_db_query_errors_total[5m])
```

## Troubleshooting

### Connection Refused

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker logs obs-postgres

# Verify network connectivity
docker exec obs-django ping obs-postgres

# Check if port is accessible
docker exec obs-django nc -zv obs-postgres 5432
```

### Authentication Failed

```bash
# Verify credentials in .env
cat django_app/.env | grep DB_

# Check PostgreSQL user exists
docker exec -it obs-postgres psql -U postgres -c "\du"

# Reset password if needed
docker exec -it obs-postgres psql -U postgres -c "ALTER USER postgres PASSWORD 'new_password';"
```

### Database Not Found

```bash
# List databases
docker exec -it obs-postgres psql -U postgres -c "\l"

# Create database if missing
docker exec -it obs-postgres psql -U postgres -c "CREATE DATABASE todo_db;"

# Check Django migrations
docker exec obs-django python manage.py showmigrations
```

### Performance Issues

```bash
# Check connection count
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check locks
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT * FROM pg_locks;"

# Check table bloat
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;"
```

### Disk Space Issues

```bash
# Check database size
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT pg_size_pretty(pg_database_size('todo_db'));"

# Check volume size
docker system df -v | grep postgres_data

# Vacuum database to reclaim space
docker exec -it obs-postgres psql -U postgres -d todo_db -c "VACUUM FULL;"
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-postgres

# Stop
docker compose -f django_app/docker-compose.yml stop obs-postgres

# Restart
docker compose -f django_app/docker-compose.yml restart obs-postgres

# View logs
docker logs -f obs-postgres

# Shell access
docker exec -it obs-postgres /bin/sh
```

### Key Paths

| Path | Description |
|------|-------------|
| `/var/lib/postgresql/data` | Database files |
| `/var/run/postgresql` | Unix socket |

### Configuration Options

| Option | Default | Purpose |
|--------|---------|---------|
| `POSTGRES_DB` | - | Initial database name |
| `POSTGRES_USER` | - | Initial superuser |
| `POSTGRES_PASSWORD` | - | Superuser password |
| `max_connections` | 100 | Maximum concurrent connections |
| `shared_buffers` | 128MB | Memory for caching |

### Connection String

```
postgresql://postgres:postgres@obs-postgres:5432/todo_db
```

### Port Mappings

| Internal Port | External Port | Purpose |
|---------------|---------------|---------|
| 5432 | 5439 | PostgreSQL database |

## Performance Tuning

### Recommended Settings

For development (default Docker setup):

```ini
# postgresql.conf (if customized)
max_connections = 100
shared_buffers = 128MB
effective_cache_size = 384MB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Connection Pooling

Django's default connection handling:
- Persistent connections (CONN_MAX_AGE)
- Connection pooling via Django ORM
- No external pooler needed for small-medium apps

### Index Optimization

```bash
# Check missing indexes
docker exec -it obs-postgres psql -U postgres -d todo_db -c "SELECT relname, seq_scan, idx_scan FROM pg_stat_user_tables WHERE seq_scan > 0 ORDER BY seq_scan DESC;"

# Reindex tables
docker exec -it obs-postgres psql -U postgres -d todo_db -c "REINDEX DATABASE todo_db;"
```

## Security Considerations

### Production Checklist

- [ ] Change default passwords
- [ ] Use strong, unique passwords
- [ ] Restrict network access (remove external port mapping)
- [ ] Enable SSL/TLS connections
- [ ] Regular backups
- [ ] Monitor connection attempts
- [ ] Keep PostgreSQL version updated

### Network Security

In production:
```yaml
# Remove external port exposure
obs-postgres:
  ports: []  # No external access
  networks:
    - app_network  # Only internal access
```

---

## Related Documentation

- [Django App](./01-django-app.md) - Application using the database
- [Prometheus](./02-prometheus.md) - Database metrics monitoring
- [Grafana](./03-grafana.md) - Database dashboards
