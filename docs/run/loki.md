# Run Loki & Promtail

Step-by-step guide to run Loki for log aggregation and Promtail for log shipping.

---

## Start

### Option 1: Start All (Recommended)

```bash
docker compose -f django_app/docker-compose.yml up -d
```

### Option 2: Start Loki & Promtail Only

```bash
# Start Loki first
docker compose -f django_app/docker-compose.yml up -d obs-loki

# Then start Promtail
docker compose -f django_app/docker-compose.yml up -d obs-promtail
```

---

## Verify

```bash
# Check containers
docker ps | grep -E "obs-loki|obs-promtail"

# Test Loki health
curl http://localhost:3100/ready
```

???+ success "Expected Output"
    ```
    ready
    ```

---

## Access

| URL | Purpose |
|-----|---------|
| http://localhost:3100 | Loki API |
| http://localhost:3100/ready | Health check |
| http://localhost:3100/metrics | Prometheus metrics |

!!! warning "No Web UI"
    Loki doesn't have a web UI. Use **Grafana** to query logs.

---

## First Steps

### 1. Push a Test Log

```bash
curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test"},"values":[["'"$(date +%s)"'000000000","test log message"]]}]}'
```

### 2. Query the Test Log

```bash
curl -s 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22test%22%7D' | jq
```

### 3. Query Django Logs

```bash
curl -s 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D' | jq '.data.result | length'
```

### 4. View in Grafana

1. Open http://localhost:3000/explore
2. Select **Loki** datasource
3. Enter query: `{app="django"}`
4. Click **Run Query**

---

## Commands

### Loki Commands

```bash
# View logs
docker logs -f obs-loki

# Access shell
docker exec -it obs-loki /bin/sh

# Check storage
docker exec obs-loki du -sh /loki/

# Test health
curl http://localhost:3100/ready

# List labels
curl http://localhost:3100/loki/api/v1/label | jq
```

### Promtail Commands

```bash
# View logs
docker logs -f obs-promtail

# Check targets
curl http://localhost:9080/targets | jq

# Verify tailing
docker logs obs-promtail | grep "Adding target"
```

### Restart

```bash
# Restart Loki
docker compose -f django_app/docker-compose.yml restart obs-loki

# Restart Promtail
docker compose -f django_app/docker-compose.yml restart obs-promtail
```

---

## Configuration

### Loki Configuration

Located at `loki/loki-config.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1

limits_config:
  retention_period: 30d
  ingestion_rate_mb: 16
```

### Promtail Configuration

Located at `promtail/promtail-config.yml`:

```yaml
server:
  http_listen_port: 9080

clients:
  - url: http://obs-loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: django
    static_configs:
      - targets: [localhost]
        labels:
          app: django
          env: dev
          __path__: /var/log/django/django.log
    pipeline_stages:
      - json:
          expressions:
            level: levelname
            logger: name
      - labels:
          level:
          logger:
```

---

## Query Examples

### LogQL Queries

```logql
# All Django logs
{app="django"}

# Error logs only
{app="django", level="ERROR"}

# Access logs
{app="django", log_type="access"}

# Search for POST requests
{app="django"} |= "POST"

# Regex search
{app="django"} |~ "(?i)error"

# Count logs per minute
count_over_time({app="django"}[1m])
```

### API Queries

```bash
# Instant query
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'

# Range query
curl 'http://localhost:3100/loki/api/v1/query_range?query=%7Bapp%3D%22django%22%7D&start=1773532800000000000&end=1773536400000000000&limit=100'

# List labels
curl http://localhost:3100/loki/api/v1/label | jq

# Label values
curl http://localhost:3100/loki/api/v1/label/app/values | jq
```

---

## Storage

Loki stores data in a Docker volume:

```bash
# Check storage
docker exec obs-loki du -sh /loki/

# View volume
docker volume inspect django_app_loki_data
```

Data retention: 30 days (configurable in loki-config.yml)

---

## Troubleshooting

??? failure "No logs in Loki"
    ```bash
    # Check Promtail is running
    docker ps | grep promtail

    # Check Promtail logs
    docker logs obs-promtail | tail -20

    # Check log file exists
    docker exec obs-django ls -la /app/logs/

    # Test push manually
    curl -X POST 'http://localhost:3100/loki/api/v1/push' \
      -H 'Content-Type: application/json' \
      -d '{"streams":[{"stream":{"app":"test"},"values":[["'"$(date +%s)"'000000000","test"]]}]}'
    ```

??? failure "Promtail not tailing"
    ```bash
    # Check volume mount
    docker inspect obs-promtail | jq '.[0].Mounts'

    # Check Promtail config
    docker exec obs-promtail cat /etc/promtail/config.yml

    # Restart Promtail
    docker compose -f django_app/docker-compose.yml restart obs-promtail
    ```

??? failure "Loki query timeout"
    ```bash
    # Reduce query limit
    curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D&limit=100'

    # Check Loki logs
    docker logs obs-loki | tail -20
    ```

---

## Stop

```bash
# Stop both
docker compose -f django_app/docker-compose.yml stop obs-loki obs-promtail

# Or stop individually
docker compose -f django_app/docker-compose.yml stop obs-loki
docker compose -f django_app/docker-compose.yml stop obs-promtail
```
