# Step 3: Log Aggregation

<div align="center" markdown>

**Learn how to centralize and search logs from all services**

</div>

---

## 📝 What Are Logs?

**Logs** are text records of events that happened in your application:

| Log Entry | What It Tells You |
|-----------|-------------------|
| `GET /todo/ 200` | User visited todo page successfully |
| `POST /todo/ 302` | User created a todo |
| `ERROR: Connection refused` | Database connection failed |

---

## 🔄 How Log Aggregation Works

### The Flow

```
Django App → Log File → Promtail → Loki → Grafana
```

1. **Django writes JSON logs** to `/app/logs/django.log`
2. **Promtail tails the file** continuously (like `tail -f`)
3. **Promtail pushes logs to Loki** via HTTP
4. **Loki stores logs** with indexed labels
5. **Grafana queries Loki** for visualization

### Key Concept: No Manual Push Needed!

???+ info "You Don't Push Logs Manually"

    Unlike some systems, you don't need to write code to push logs. The flow is:

    ```
    You write: logger.info("message")
         ↓
    Django writes JSON to file
         ↓
    Promtail tails file automatically
         ↓
    Promtail pushes to Loki automatically
         ↓
    Logs appear in Grafana
    ```

    **You just call `logger.info()` - everything else is automatic!**

---

## 🔍 Viewing Logs

### Option 1: View in Grafana (Recommended)

1. Open http://localhost:3000
2. Click "Explore"
3. Select "Loki" datasource
4. Enter a query:

```logql
{app="django"}
```

5. Click "Run Query"
6. You'll see all Django logs!

### Option 2: Query Loki API Directly

```bash
# Query all Django logs
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'

# Query error logs only
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22,level%3D%22ERROR%22%7D'
```

### Option 3: View Log File Directly

```bash
# View log file
docker exec obs-django cat /app/logs/django.log | tail -10

# Follow log file
docker exec -it obs-django tail -f /app/logs/django.log
```

---

## 🎯 LogQL Queries

LogQL is Loki's query language. Here are common queries:

### Basic Queries

```logql
# All Django logs
{app="django"}

# Error logs only
{app="django", level="ERROR"}

# Access logs
{app="django", log_type="access"}

# Error logs from Gunicorn
{app="django", log_type="error"}
```

### Search Queries

```logql
# Logs containing "POST"
{app="django"} |= "POST"

# Logs containing "error" (case insensitive)
{app="django"} |~ "(?i)error"

# Logs from specific endpoint
{app="django"} |= "/todo/"
```

### Aggregation Queries

```logql
# Count logs per minute
count_over_time({app="django"}[1m])

# Rate of logs per second
rate({app="django"}[5m])
```

---

## 🔬 Hands-On Exercises

### Exercise 1: Generate Some Logs

```bash
# Make requests to generate logs
for i in {1..5}; do
  curl -s http://localhost/ > /dev/null
  echo "Request $i sent"
done

# Generate a 404 error
curl -s http://localhost/nonexistent-page > /dev/null

# Check logs
docker exec obs-django cat /app/logs/django.log | tail -10
```

### Exercise 2: Query Logs in Grafana

1. Open http://localhost:3000/explore
2. Select Loki datasource
3. Try these queries:

```logql
# All logs
{app="django"}

# Only errors
{app="django", level="ERROR"}

# Search for "GET"
{app="django"} |= "GET"
```

### Exercise 3: View Promtail Status

```bash
# Check Promtail is running
docker ps | grep promtail

# View Promtail logs
docker logs obs-promtail --tail 20
```

---

## 📊 Understanding the Log Format

Django writes logs in JSON format:

```json
{
  "asctime": "2026-03-15T10:30:45",
  "levelname": "INFO",
  "name": "django",
  "message": "GET /todo/ 200"
}
```

Promtail parses this and extracts labels:

| JSON Field | Label | Purpose |
|------------|-------|---------|
| `levelname` | `level` | Filter by log level |
| `name` | `logger` | Filter by logger |
| `message` | `message` | The actual log content |

---

## 🔧 Troubleshooting

??? failure "No logs in Loki"

    **Check if log file exists:**

    ```bash
    docker exec obs-django ls -la /app/logs/
    ```

    **Check Promtail is tailing:**

    ```bash
    docker logs obs-promtail | grep "django.log"
    ```

    **Test push manually:**

    ```bash
    curl -X POST 'http://localhost:3100/loki/api/v1/push' \
      -H 'Content-Type: application/json' \
      -d '{"streams":[{"stream":{"app":"test"},"values":[["'"$(date +%s)"'000000000","test"]]}]}'

    # Query test logs
    curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22test%22%7D'
    ```

??? failure "Promtail not seeing new logs"

    **Check volume mount:**

    ```bash
    docker inspect obs-promtail | jq '.[0].Mounts'
    ```

    **Restart Promtail:**

    ```bash
    docker compose -f django_app/docker-compose.yml restart obs-promtail
    ```

---

## 📚 What You Learned

In this step, you learned:

- ✅ How logs flow from Django → Promtail → Loki
- ✅ How to query logs with LogQL
- ✅ How to view logs in Grafana
- ✅ How Promtail automatically pushes logs
- ✅ How to search and filter logs

---

## 🎓 Next Steps

Now that you understand logs, let's learn about alerts:

- [Loki Module](../modules/04-loki.md) - Advanced LogQL queries
- [Promtail Module](../modules/05-promtail.md) - Customize log shipping
- [Alertmanager Module](../modules/06-alertmanager.md) - Set up alerts

---

<div align="center" markdown>

**Ready for Step 4?** 👇

[Step 4: Alerts →](alerts.md){ .md-button .md-button--primary }

</div>
