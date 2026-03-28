# Step 2: Understanding Metrics

<div align="center" markdown>

**Learn how Prometheus collects and stores metrics from your Django app**

</div>

---

## 📊 What Are Metrics?

**Metrics** are numeric measurements that help you understand your application's behavior:

| Metric Type | Example | What It Tells You |
|-------------|---------|-------------------|
| **Counter** | `django_http_requests_total` | Total number of requests |
| **Histogram** | `django_http_requests_latency_seconds` | Distribution of request times |
| **Gauge** | `node_memory_MemAvailable_bytes` | Current memory usage |

---

## 🔍 How Metrics Work

### Step 1: Django Exposes Metrics

Django automatically exposes metrics at `/metrics`:

```bash
# View Django metrics
curl http://localhost:9000/metrics | head -20
```

You'll see output like:

```
# HELP django_http_requests_total Total number of HTTP requests
# TYPE django_http_requests_total counter
django_http_requests_total{method="GET",status="200",view="/todo/"} 42.0

# HELP django_http_requests_latency_seconds HTTP request latency
# TYPE django_http_requests_latency_seconds histogram
django_http_requests_latency_seconds_bucket{le="0.005",method="GET"} 30.0
```

### Step 2: Prometheus Scrapes Metrics

Prometheus automatically scrapes metrics every 15 seconds:

```yaml
# prometheus/prometheus.yml
scrape_configs:
  - job_name: "django"
    static_configs:
      - targets: ["obs-django:9000"]
    metrics_path: /metrics
```

### Step 3: Query Metrics in Prometheus

Open Prometheus UI: http://localhost:9090

Try these PromQL queries:

```promql
# Check if Django is up
up{job="django"}

# Request rate (requests per second)
rate(django_http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m]))

# Database query rate
rate(django_db_execute_total[5m])
```

---

## 🎯 Key Metrics to Monitor

### HTTP Metrics

| Metric | Description | Query |
|--------|-------------|-------|
| `django_http_requests_total` | Total requests | `sum(rate(django_http_requests_total[5m]))` |
| `django_http_requests_latency_seconds` | Request duration | `histogram_quantile(0.95, rate(...[5m]))` |
| `django_http_responses_total_by_status` | Response status codes | `sum by (status) (rate(...[5m]))` |

### Database Metrics

| Metric | Description | Query |
|--------|-------------|-------|
| `django_db_query_duration_seconds` | Query duration | `histogram_quantile(0.95, rate(...[5m]))` |
| `django_db_errors_total` | DB errors | `rate(django_db_errors_total[5m])` |
| `django_db_execute_total` | Total queries | `rate(django_db_execute_total[5m])` |

### System Metrics

| Metric | Description | Query |
|--------|-------------|-------|
| `node_cpu_seconds_total` | CPU usage | `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` |
| `node_memory_MemAvailable_bytes` | Available memory | `node_memory_MemAvailable_bytes` |
| `node_filesystem_avail_bytes` | Available disk | `node_filesystem_avail_bytes` |

---

## 🔬 Hands-On Exercises

### Exercise 1: Generate Traffic

Create some requests to generate metrics:

```bash
# Make 10 requests to the home page
for i in {1..10}; do
  curl -s http://localhost/ > /dev/null
  echo "Request $i sent"
done

# Make requests to the todo page
for i in {1..5}; do
  curl -s http://localhost/todo/ > /dev/null
  echo "Todo request $i sent"
done
```

### Exercise 2: Query Prometheus

Open http://localhost:9090 and run these queries:

```promql
# See total requests
sum(django_http_requests_total)

# See request rate over last 5 minutes
sum(rate(django_http_requests_total[5m]))

# See requests by status code
sum by (status) (rate(django_http_requests_total[5m]))
```

### Exercise 3: Check Target Health

1. Go to http://localhost:9090/targets
2. Look at the "django" target
3. Verify it shows "UP" status

---

## 📈 Visualizing in Grafana

1. Open http://localhost:3000
2. Login with admin/admin
3. Click "Explore"
4. Select "Prometheus" datasource
5. Enter a query:

```promql
rate(django_http_requests_total[5m])
```

6. Click "Run Query"
7. You'll see a graph of request rates!

---

## 🔧 Troubleshooting

??? failure "No metrics appearing"

    **Check if Django is exposing metrics:**

    ```bash
    curl http://localhost:9000/metrics | head
    ```

    **Check if Prometheus can reach Django:**

    ```bash
    docker exec obs-prometheus wget -qO- http://obs-django:9000/metrics | head
    ```

    **Check Prometheus targets:**

    ```bash
    curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="django")'
    ```

??? failure "Prometheus shows target as DOWN"

    **Verify containers are on same network:**

    ```bash
    docker network inspect django_app_observability_network | grep -A5 obs-django
    ```

    **Restart Prometheus:**

    ```bash
    docker compose -f django_app/docker-compose.yml restart obs-prometheus
    ```

---

## 📚 What You Learned

In this step, you learned:

- ✅ How Django exposes metrics at `/metrics`
- ✅ How Prometheus scrapes metrics every 15 seconds
- ✅ How to query metrics with PromQL
- ✅ Key metrics to monitor (HTTP, DB, System)
- ✅ How to visualize metrics in Grafana

---

## 🎓 Next Steps

Now that you understand metrics, let's learn about logs:

- [Django App Module](../modules/01-django-app.md) - Deep dive into Django metrics
- [Prometheus Module](../modules/02-prometheus.md) - Advanced PromQL queries
- [Grafana Module](../modules/03-grafana.md) - Create custom dashboards

---

<div align="center" markdown>

**Ready for Step 3?** 👇

[Step 3: Logs →](logs.md){ .md-button .md-button--primary }

</div>
