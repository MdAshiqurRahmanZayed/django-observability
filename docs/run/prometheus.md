# Run Prometheus

Step-by-step guide to run Prometheus for metrics collection.

---

## Start

### Option 1: Start All (Recommended)

```bash
docker compose -f django_app/docker-compose.yml up -d
```

### Option 2: Start Prometheus Only

```bash
docker compose -f django_app/docker-compose.yml up -d obs-prometheus
```

---

## Verify

```bash
# Check container
docker ps | grep obs-prometheus

# Test health
curl http://localhost:9090/-/healthy
```

???+ success "Expected Output"
    ```
    Prometheus Server is Healthy.
    ```

---

## Access

| URL | Purpose |
|-----|---------|
| http://localhost:9090 | Prometheus UI |
| http://localhost:9090/targets | Scrape targets |
| http://localhost:9090/graph | PromQL query interface |
| http://localhost:9090/alerts | Alert rules |
| http://localhost:9090/metrics | Prometheus own metrics |

---

## First Steps

### 1. Check Targets

1. Open http://localhost:9090/targets
2. Verify all targets show "UP" status:
   - prometheus (localhost:9090)
   - django (obs-django:9000)
   - node (obs-node-exporter:9100)
   - loki (obs-loki:3100)
   - grafana (obs-grafana:3000)

### 2. Run First Query

1. Open http://localhost:9090/graph
2. Enter query: `up`
3. Click "Execute"
4. You should see all targets with value `1`

### 3. Explore Metrics

Try these queries:

```promql
# Target status
up

# Django request rate
rate(django_http_requests_total[5m])

# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
```

---

## Commands

### View Logs

```bash
docker logs -f obs-prometheus
```

### Access Shell

```bash
docker exec -it obs-prometheus /bin/sh
```

### Query via API

```bash
# Instant query
curl 'http://localhost:9090/api/v1/query?query=up'

# Range query
curl 'http://localhost:9090/api/v1/query_range?query=up&start=1773532800&end=1773536400&step=60s'

# List targets
curl http://localhost:9090/api/v1/targets | jq

# List alert rules
curl http://localhost:9090/api/v1/rules | jq
```

### Reload Configuration

```bash
# After editing prometheus.yml
docker exec obs-prometheus kill -HUP 1
```

### Restart

```bash
docker compose -f django_app/docker-compose.yml restart obs-prometheus
```

---

## Configuration

### prometheus.yml

Located at `prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s      # How often to scrape
  evaluation_interval: 15s  # How often to evaluate rules

scrape_configs:
  - job_name: "django"
    static_configs:
      - targets: ["obs-django:9000"]
    metrics_path: /metrics

  - job_name: "node"
    static_configs:
      - targets: ["obs-node-exporter:9100"]

  - job_name: "loki"
    static_configs:
      - targets: ["obs-loki:3100"]
    metrics_path: /metrics

  - job_name: "grafana"
    static_configs:
      - targets: ["obs-grafana:3000"]
    metrics_path: /metrics
```

### Alert Rules

Located at `prometheus/rules/alerts.yml`:

```yaml
groups:
  - name: db_alerts
    rules:
      - alert: DBHighErrorRate
        expr: rate(django_db_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High DB error rate"
```

---

## Storage

Prometheus stores data in a Docker volume:

```bash
# Check storage usage
docker exec obs-prometheus du -sh /prometheus

# View volume
docker volume inspect django_app_prometheus_data
```

Data retention: 15 days (configurable in docker-compose.yml)

---

## Troubleshooting

??? failure "Target shows DOWN"
    ```bash
    # Check target can be reached
    docker exec obs-prometheus wget -qO- http://obs-django:9000/metrics

    # Check network
    docker network inspect django_app_observability_network

    # Restart target service
    docker compose -f django_app/docker-compose.yml restart obs-django
    ```

??? failure "No data in queries"
    ```bash
    # Check if metrics exist
    curl http://localhost:9090/api/v1/query?query=up

    # Wait 15 seconds for first scrape
    sleep 15

    # Check scrape logs
    docker logs obs-prometheus | grep "scrape"
    ```

??? failure "Alerts not firing"
    ```bash
    # Check rules are loaded
    curl http://localhost:9090/api/v1/rules | jq

    # Check alert states
    curl http://localhost:9090/api/v1/alerts | jq

    # Verify Alertmanager is reachable
    docker exec obs-prometheus wget -qO- http://obs-alertmanager:9093/-/healthy
    ```

---

## Stop

```bash
docker compose -f django_app/docker-compose.yml stop obs-prometheus
```
