# Step 4: Setting Up Alerts

<div align="center" markdown>

**Learn how to get notified when things go wrong**

</div>

---

## 🔔 What Are Alerts?

**Alerts** notify you when your application has problems:

| Alert | When It Fires |
|-------|---------------|
| **DjangoDown** | Django is unreachable |
| **High5xxRate** | Too many server errors |
| **HighCPUUsage** | CPU usage > 85% |
| **DBSlowQueries** | Database queries taking too long |

---

## 🔄 How Alerts Work

```
Prometheus (evaluates rules) → Alertmanager (routes) → Slack (notifies)
```

1. **Prometheus** evaluates alert rules every 15 seconds
2. If condition met, alert is sent to **Alertmanager**
3. **Alertmanager** groups and routes alerts
4. **Slack** receives formatted notification

---

## 📋 Default Alert Rules

This stack includes these alerts:

### Database Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `DBHighErrorRate` | DB errors > 0.1/s | Critical |
| `DBSlowQueries` | p95 query time > 1s | Warning |
| `DBHighQueryRate` | Queries > 100/s | Warning |

### HTTP Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `DjangoDown` | Target unreachable | Critical |
| `Django5xxError` | Any 5xx response | Critical |
| `Django4xxError` | Any 4xx response | Warning |
| `HighHTTP5xxRate` | 5xx errors > 0.5/s | Critical |

### Infrastructure Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| `HighCPUUsage` | CPU > 85% | Warning |
| `CriticalCPUUsage` | CPU > 95% | Critical |
| `HighMemoryUsage` | Memory > 85% | Warning |
| `HighDiskUsage` | Disk > 85% | Warning |

---

## 🧪 Testing Alerts

### View Alert Rules in Prometheus

1. Open http://localhost:9090/alerts
2. You'll see all configured alert rules
3. Check their current state (Inactive/Firing)

### View Alertmanager

1. Open http://localhost:9093
2. You'll see alert routing configuration
3. Check active alerts

### Trigger a Test Alert

```bash
# Stop Django to trigger DjangoDown alert
docker compose -f django_app/docker-compose.yml stop obs-django

# Wait 30 seconds, then check Alertmanager
curl http://localhost:9093/api/v1/alerts | jq

# Start Django again
docker compose -f django_app/docker-compose.yml start obs-django
```

---

## ⚙️ Configuring Slack Alerts

### Step 1: Get Slack Webhook URL

1. Go to https://api.slack.com/apps
2. Create a new app
3. Add "Incoming Webhooks" feature
4. Create webhook for your channel
5. Copy the webhook URL

### Step 2: Add to Environment

Edit `django_app/.env`:

```bash
SLACK_WEBHOOK_URL=See https://api.slack.com/apps to get your webhook URL
```

### Step 3: Restart Alertmanager

```bash
docker compose -f django_app/docker-compose.yml restart obs-alertmanager
```

### Step 4: Test Alert

```bash
# Stop Django to trigger alert
docker compose -f django_app/docker-compose.yml stop obs-django

# Check Slack for notification!
```

---

## 🔧 Troubleshooting

??? failure "Alerts not firing"

    **Check Prometheus rules:**

    ```bash
    curl http://localhost:9090/api/v1/rules | jq
    ```

    **Check alert state:**

    ```bash
    curl http://localhost:9090/api/v1/alerts | jq
    ```

??? failure "Slack notifications not working"

    **Check webhook URL:**

    ```bash
    grep SLACK_WEBHOOK_URL django_app/.env
    ```

    **Test webhook manually:**

    ```bash
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"Test alert"}' $SLACK_WEBHOOK_URL
    ```

---

## 📚 What You Learned

In this step, you learned:

- ✅ How alerts work in the stack
- ✅ Default alert rules configured
- ✅ How to test alerts
- ✅ How to configure Slack notifications

---

## 🎓 Next Steps

Now that you understand alerts, let's create dashboards:

- [Alertmanager Module](../modules/06-alertmanager.md) - Advanced alert routing
- [Prometheus Module](../modules/02-prometheus.md) - Create custom alerts

---

<div align="center" markdown>

**Ready for Step 5?** 👇

[Step 5: Visualization →](visualization.md){ .md-button .md-button--primary }

</div>
