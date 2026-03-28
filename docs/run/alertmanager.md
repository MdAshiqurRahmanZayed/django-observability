# Run Alertmanager

Step-by-step guide to run Alertmanager for alert routing and notifications.

---

## Start

### Option 1: Start All (Recommended)

```bash
docker compose -f django_app/docker-compose.yml up -d
```

### Option 2: Start Alertmanager Only

```bash
docker compose -f django_app/docker-compose.yml up -d obs-alertmanager
```

---

## Verify

```bash
# Check container
docker ps | grep obs-alertmanager

# Test health
curl http://localhost:9093/-/healthy
```

???+ success "Expected Output"
    ```
    OK
    ```

---

## Access

| URL | Purpose |
|-----|---------|
| http://localhost:9093 | Alertmanager UI |
| http://localhost:9093/#/alerts | Active alerts |
| http://localhost:9093/#/status | Configuration |

---

## First Steps

### 1. Check Configuration

1. Open http://localhost:9093/#/status
2. Review the routing configuration

### 2. View Alert Rules

1. Open http://localhost:9090/alerts (Prometheus)
2. See all configured alert rules

### 3. Test an Alert

```bash
# Stop Django to trigger alert
docker compose -f django_app/docker-compose.yml stop obs-django

# Wait 30 seconds
sleep 30

# Check Alertmanager for firing alert
curl http://localhost:9093/api/v1/alerts | jq

# Start Django again
docker compose -f django_app/docker-compose.yml start obs-django
```

---

## Commands

### View Logs

```bash
docker logs -f obs-alertmanager
```

### Access Shell

```bash
docker exec -it obs-alertmanager /bin/sh
```

### API Queries

```bash
# List active alerts
curl http://localhost:9093/api/v1/alerts | jq

# Get status
curl http://localhost:9093/api/v1/status | jq

# Get receivers
curl http://localhost:9093/api/v1/status | jq '.config.receivers'
```

### Restart

```bash
docker compose -f django_app/docker-compose.yml restart obs-alertmanager
```

---

## Configuration

Located at `alertmanager/alertmanager.yml`:

```yaml
global:
  resolve_timeout: 5m
  slack_api_url: "SLACK_WEBHOOK_URL_PLACEHOLDER"

route:
  group_by: ["alertname", "category"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: "slack-default"
  routes:
    - match:
        category: db
      receiver: "slack-db"
    - match:
        category: http
      receiver: "slack-http"
    - match:
        category: latency
      receiver: "slack-latency"
    - match:
        category: infrastructure
      receiver: "slack-infra"

receivers:
  - name: "slack-default"
    slack_configs:
      - channel: "#alerts"
        send_resolved: true
  - name: "slack-db"
    slack_configs:
      - channel: "#alerts-db"
  - name: "slack-http"
    slack_configs:
      - channel: "#alerts-http"
  - name: "slack-latency"
    slack_configs:
      - channel: "#alerts-latency"
  - name: "slack-infra"
    slack_configs:
      - channel: "#alerts-infra"
```

---

## Configure Slack Notifications

### Step 1: Get Webhook URL

1. Go to https://api.slack.com/apps
2. Create new app or select existing
3. Enable **Incoming Webhooks**
4. Create webhook for your channel
5. Copy the webhook URL

### Step 2: Add to Environment

Edit `django_app/.env`:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 3: Restart Alertmanager

```bash
docker compose -f django_app/docker-compose.yml restart obs-alertmanager
```

### Step 4: Test

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert from observability stack"}' \
  $SLACK_WEBHOOK_URL
```

---

## Alert Categories

| Category | Slack Channel | Example Alerts |
|----------|---------------|----------------|
| db | #alerts-db | DBHighErrorRate, DBSlowQueries |
| http | #alerts-http | DjangoDown, Django5xxError |
| latency | #alerts-latency | HighP95Latency, HighP99Latency |
| infrastructure | #alerts-infra | HighCPUUsage, HighMemoryUsage |

---

## Troubleshooting

??? failure "No alerts appearing"
    ```bash
    # Check Prometheus has rules
    curl http://localhost:9090/api/v1/rules | jq

    # Check Alertmanager is configured in Prometheus
    curl http://localhost:9090/api/v1/alertmanagers | jq

    # Check Alertmanager logs
    docker logs obs-alertmanager | tail -20
    ```

??? failure "Slack notifications not working"
    ```bash
    # Check webhook URL is set
    docker exec obs-alertmanager env | grep SLACK

    # Test webhook manually
    curl -X POST -H 'Content-type: application/json' \
      --data '{"text":"Test"}' \
      $SLACK_WEBHOOK_URL

    # Check Alertmanager receiver config
    curl http://localhost:9093/api/v1/status | jq '.config.receivers'
    ```

??? failure "Alerts firing but not sending"
    ```bash
    # Check routing
    curl http://localhost:9093/api/v1/status | jq '.config.route'

    # Check group_wait setting (may need to wait)
    # Default is 30s
    ```

---

## Stop

```bash
docker compose -f django_app/docker-compose.yml stop obs-alertmanager
```
