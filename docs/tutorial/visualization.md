# Step 5: Visualization with Grafana

<div align="center" markdown>

**Learn how to create beautiful dashboards to understand your app**

</div>

---

## 📊 What is Grafana?

**Grafana** is a visualization platform that creates dashboards from your metrics and logs:

| Feature | What It Does |
|---------|--------------|
| **Dashboards** | Visual panels showing metrics |
| **Explore** | Ad-hoc queries for debugging |
| **Alerting** | Visual alert rules |
| **Datasources** | Connect to Prometheus, Loki |

---

## 🌐 Accessing Grafana

1. Open http://localhost:3000
2. Login with:
   - **Username**: admin
   - **Password**: admin

---

## 🔍 Using Explore

Explore is great for ad-hoc queries:

### Query Prometheus (Metrics)

1. Click "Explore" in sidebar
2. Select "Prometheus" datasource
3. Enter a PromQL query:

```promql
# Request rate
rate(django_http_requests_total[5m])

# Latency
histogram_quantile(0.95, rate(django_http_requests_latency_seconds_bucket[5m]))

# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

4. Click "Run Query"

### Query Loki (Logs)

1. Click "Explore" in sidebar
2. Select "Loki" datasource
3. Enter a LogQL query:

```logql
# All Django logs
{app="django"}

# Error logs
{app="django", level="ERROR"}

# Search logs
{app="django"} |= "POST"
```

4. Click "Run Query"

---

## 📈 Creating Your First Dashboard

### Step 1: Create Dashboard

1. Click "Dashboards" in sidebar
2. Click "New Dashboard"
3. Click "Add visualization"
4. Select "Prometheus" datasource

### Step 2: Add Request Rate Panel

1. Enter query:

```promql
sum(rate(django_http_requests_total[5m]))
```

2. Click "Run Query"
3. In panel options:
   - Title: "Request Rate"
   - Unit: "requests/sec"
4. Click "Apply"

### Step 3: Add Latency Panel

1. Click "Add panel"
2. Enter query:

```promql
histogram_quantile(0.95, 
  sum(rate(django_http_requests_latency_seconds_bucket[5m])) by (le)
)
```

3. Set title: "P95 Latency"
4. Set unit: "seconds"
5. Click "Apply"

### Step 4: Add Error Rate Panel

1. Click "Add panel"
2. Enter query:

```promql
sum(rate(django_http_responses_total_by_status_total{status=~"5.."}[5m]))
```

3. Set title: "5xx Error Rate"
4. Set unit: "errors/sec"
5. Click "Apply"

### Step 5: Save Dashboard

1. Click "Save dashboard" (disk icon)
2. Name: "My Django Dashboard"
3. Click "Save"

---

## 🎨 Dashboard Best Practices

### Layout Tips

```
┌─────────────────────────────────────────────────────────────────┐
│  Row 1: Key Metrics (Request Rate, Latency, Errors)            │
├─────────────────────────────────────────────────────────────────┤
│  Row 2: Resource Metrics (CPU, Memory, Disk)                   │
├─────────────────────────────────────────────────────────────────┤
│  Row 3: Database Metrics (Query Time, Connections)             │
├─────────────────────────────────────────────────────────────────┤
│  Row 4: Logs (Recent errors, Recent requests)                  │
└─────────────────────────────────────────────────────────────────┘
```

### Panel Types

| Type | Best For |
|------|----------|
| **Graph** | Time-series data (rates, latencies) |
| **Stat** | Single value (current CPU, total requests) |
| **Table** | Detailed data (top endpoints) |
| **Logs** | Log entries |

---

## 🔬 Hands-On Exercise

### Create a Complete Dashboard

1. **Request Rate** - `sum(rate(django_http_requests_total[5m]))`
2. **P95 Latency** - `histogram_quantile(0.95, sum(rate(django_http_requests_latency_seconds_bucket[5m])) by (le))`
3. **Error Rate** - `sum(rate(django_http_responses_total_by_status_total{status=~"5.."}[5m]))`
4. **CPU Usage** - `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`
5. **Memory Usage** - `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100`
6. **Recent Logs** - `{app="django", level="ERROR"}`

---

## 🔧 Troubleshooting

??? failure "No data in panels"
    
    **Check datasource:**
    
    1. Go to Configuration → Data Sources
    2. Verify Prometheus URL: `http://obs-prometheus:9090`
    3. Click "Save & Test"
    
    **Check if metrics exist:**
    
    ```bash
    curl http://localhost:9090/api/v1/query?query=up
    ```

??? failure "Loki datasource not working"
    
    **Verify Loki datasource:**
    
    1. Go to Configuration → Data Sources
    2. Click Loki datasource
    3. URL should be: `http://obs-loki:3100`
    4. Click "Save & Test"

---

## 📚 What You Learned

In this step, you learned:

- ✅ How to access and login to Grafana
- ✅ How to use Explore for ad-hoc queries
- ✅ How to create dashboards
- ✅ How to add panels for metrics and logs
- ✅ Dashboard best practices

---

## 🎉 Tutorial Complete!

Congratulations! You've completed the Django Observability tutorial. You now know how to:

1. ✅ **Set up** the observability stack
2. ✅ **Monitor metrics** with Prometheus
3. ✅ **Aggregate logs** with Loki
4. ✅ **Set up alerts** with Alertmanager
5. ✅ **Visualize data** with Grafana

---

## 🎓 Continue Learning

Explore the detailed module documentation:

| Module | What You'll Learn |
|--------|-------------------|
| [Django App](../modules/01-django-app.md) | Deep dive into metrics & logging |
| [Prometheus](../modules/02-prometheus.md) | Advanced PromQL queries |
| [Grafana](../modules/03-grafana.md) | Advanced dashboards |
| [Loki](../modules/04-loki.md) | Advanced LogQL queries |
| [Alertmanager](../modules/06-alertmanager.md) | Advanced alert routing |
| [MCP Server](../modules/08-mcp-server.md) | AI integration |

---

<div align="center" markdown>

**Thank you for following the tutorial!** 🎉

[View All Modules →](../modules/01-django-app.md){ .md-button .md-button--primary }

</div>
