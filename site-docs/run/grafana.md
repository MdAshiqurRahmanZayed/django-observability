# Run Grafana

Step-by-step guide to run Grafana for visualization.

---

## Start

### Option 1: Start All (Recommended)

```bash
docker compose -f django_app/docker-compose.yml up -d
```

### Option 2: Start Grafana Only

```bash
docker compose -f django_app/docker-compose.yml up -d obs-grafana
```

---

## Verify

```bash
# Check container
docker ps | grep obs-grafana

# Test health
curl http://localhost:3000/api/health
```

???+ success "Expected Output"
    ```json
    {"database":"ok"}
    ```

---

## Login

1. Open http://localhost:3000
2. Login credentials:
   - **Username**: `admin`
   - **Password**: `admin`
3. Optionally change password on first login

---

## Access

| URL | Purpose |
|-----|---------|
| http://localhost:3000 | Grafana home |
| http://localhost:3000/explore | Query interface |
| http://localhost:3000/dashboards | Browse dashboards |
| http://localhost:3000/alerting | Alert rules |

---

## First Steps

### 1. Check Datasources

1. Go to **Configuration** → **Data Sources**
2. Verify two datasources exist:
   - **Prometheus** (default) → `http://obs-prometheus:9090`
   - **Loki** → `http://obs-loki:3100`

### 2. Query Prometheus (Metrics)

1. Click **Explore** in sidebar
2. Select **Prometheus** from dropdown
3. Enter query:
   ```promql
   rate(django_http_requests_total[5m])
   ```
4. Click **Run Query**
5. See the graph!

### 3. Query Loki (Logs)

1. Click **Explore** in sidebar
2. Select **Loki** from dropdown
3. Enter query:
   ```logql
   {app="django"}
   ```
4. Click **Run Query**
5. See the logs!

---

## Commands

### View Logs

```bash
docker logs -f obs-grafana
```

### Access Shell

```bash
docker exec -it obs-grafana /bin/sh
```

### API Queries

```bash
# Health check
curl http://localhost:3000/api/health

# List datasources
curl -u admin:admin http://localhost:3000/api/datasources | jq

# List dashboards
curl -u admin:admin http://localhost:3000/api/search | jq

# Query Prometheus via Grafana
curl -u admin:admin 'http://localhost:3000/api/datasources/uid/prometheus/api/v1/query?query=up'
```

### Restart

```bash
docker compose -f django_app/docker-compose.yml restart obs-grafana
```

---

## Configuration

### Datasources (Auto-provisioned)

Located at `grafana/provisioning/datasources/datasources.yml`:

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://obs-prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://obs-loki:3100
```

### Environment Variables

From `django_app/.env`:

```bash
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin
```

---

## Creating Dashboards

### Quick Dashboard

1. Click **Dashboards** → **New Dashboard**
2. Click **Add visualization**
3. Select **Prometheus** datasource
4. Enter query:
   ```promql
   sum(rate(django_http_requests_total[5m]))
   ```
5. Click **Apply**
6. Click **Save dashboard**

### Add More Panels

| Panel | Query |
|-------|-------|
| Request Rate | `sum(rate(django_http_requests_total[5m]))` |
| P95 Latency | `histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_bucket[5m])) by (le))` |
| Error Rate | `sum(rate(django_http_responses_total_by_status_total{status=~"5.."}[5m]))` |
| CPU Usage | `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| Memory | `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100` |

---

## Storage

Grafana stores data in a Docker volume:

```bash
docker volume inspect django_app_grafana_data
```

---

## Troubleshooting

??? failure "Cannot login"
    ```bash
    # Reset password via environment
    # Edit .env:
    GF_ADMIN_PASSWORD=newpassword
    
    # Restart
    docker compose -f django_app/docker-compose.yml restart obs-grafana
    ```

??? failure "Datasource connection failed"
    ```bash
    # Test Prometheus from Grafana
    docker exec obs-grafana wget -qO- http://obs-prometheus:9090/-/healthy
    
    # Test Loki from Grafana
    docker exec obs-grafana wget -qO- http://obs-loki:3100/ready
    
    # Check datasources config
    docker exec obs-grafana cat /etc/grafana/provisioning/datasources/datasources.yml
    ```

??? failure "No data in panels"
    ```bash
    # Verify Prometheus has data
    curl http://localhost:9090/api/v1/query?query=up
    
    # Check Grafana logs
    docker logs obs-grafana | tail -20
    ```

---

## Stop

```bash
docker compose -f django_app/docker-compose.yml stop obs-grafana
```
