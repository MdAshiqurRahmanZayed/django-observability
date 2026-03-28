# Screenshots Gallery

This page showcases all the screenshots from the Django Observability Stack. Use the tabs below to browse by category.

---

## 📊 Grafana Dashboards

=== "Overview"

    ![Grafana Overview](assets/grafana/grafana-overview.png)

    **Main Dashboard** - Overview of all services and metrics

=== "Django Metrics"

    ![Django Overview](assets/grafana/django-overview.png)

    **Django Dashboard** - HTTP requests, latency, and errors

=== "Grafana Dashboard"

    ![Grafana Dashboard](assets/grafana/grafana-dashaboard.png)

    **Detailed View** - Custom Grafana dashboard configuration

=== "Infrastructure"

    ![Infrastructure Overview](assets/grafana/infra-overview.png)

    **Infrastructure Dashboard** - CPU, memory, and disk usage

=== "Loki Logs"

    ![Loki Overview](assets/grafana/loki-overview.png)

    **Loki Dashboard** - Log aggregation and search

=== "Nginx"

    ![Nginx Overview](assets/grafana/nginx-overview.png)

    **Nginx Dashboard** - Reverse proxy metrics

---

## 📝 Application

=== "Todo App"

    ![Main Todos](assets/main/main-todos.png)

    **Todo Application** - Django app being monitored

---

## 🤖 MCP Server

=== "Server Status"

    ![MCP Server Status](assets/mcp/server-status.png)

    **MCP Server** - Health check and service status

=== "Latest Todos"

    ![Get Latest Todos](assets/mcp/get-latest-todos.png)

    **MCP Tool** - Fetching latest todos via MCP server

---

## 📈 Prometheus

=== "Overview"

    ![Prometheus Overview](assets/prometheus/prometheus-overview.png)

    **Prometheus UI** - Main metrics dashboard

=== "Alerts"

    ![Prometheus Alerts](assets/prometheus/prometheus-alert.png)

    **Alert Rules** - Configured alert rules in Prometheus

=== "Alertmanager"

    ![Alertmanager](assets/prometheus/prometheus-alert-manager.png)

    **Alertmanager UI** - Alert routing and notifications

=== "Health Status"

    ![Prometheus Health](assets/prometheus/prometheus-status-health.png)

    **Health Status** - Target health monitoring

---

## 🎨 What You'll See

When you run the stack, you'll have access to:

| Feature | What It Shows |
|---------|---------------|
| **Grafana Dashboards** | Real-time metrics visualization |
| **Prometheus UI** | Raw metrics and PromQL queries |
| **Alertmanager** | Alert status and routing |
| **Loki/LogQL** | Log search and analysis |
| **MCP Server** | AI-powered insights |

---

## 📱 Taking Your Own Screenshots

Want to capture your own screenshots? Here's how:

### Grafana

1. Open <http://localhost:3000>
2. Login with admin/admin
3. Navigate to Dashboards
4. Press `Cmd+Shift+4` (Mac) or `Win+Shift+S` (Windows)

### Prometheus

1. Open <http://localhost:9090>
2. Go to Status → Targets
3. Take screenshot of target health

### Application

1. Open <http://localhost>
2. Create some todos
3. Take screenshot of the app

---

<div align="center" markdown>

**Ready to explore?** 👇

[Start Tutorial](getting-started.md){ .md-button .md-button--primary }

</div>
