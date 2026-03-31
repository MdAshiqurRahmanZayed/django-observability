# Loki

## Overview

Loki is a horizontally-scalable, highly-available log aggregation system designed to store and query logs from all your applications. Unlike traditional log systems that index full text, Loki indexes only metadata (labels) making it more efficient and cost-effective.

## Description

Loki is like Prometheus but for logs. It uses the same principles:
- **Pull model** (Promtail pushes, Loki stores)
- **Label-based indexing** (not full-text search)
- **LogQL** query language (similar to PromQL)

In this stack, Loki:
- Receives logs from Promtail via HTTP push
- Stores log lines with labels
- Serves log queries via API
- Integrates with Grafana for visualization

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LOKI IN STACK                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   LOG PUSH (Push Model)                                                     │
│   ────────────────────                                                      │
│                                                                             │
│   ┌─────────────┐     POST /loki/api/v1/push     ┌─────────────┐            │
│   │   Promtail  │ ──────────────────────────────▶│    Loki     │            │
│   │  (agent)    │                                │    :3100    │            │
│   └─────────────┘                                └──────┬──────┘            │
│                                                         │                   │
│   LOG QUERY                                             │                   │
│   ─────────                                             │                   │
│                                                         ▼                   │
│                                          ┌─────────────────────────┐        │
│                                          │       Grafana           │        │
│                                          │         :3000           │        │
│                                          └─────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Log Storage | Loki | 2.9.0 |
| Index | TSDB (built-in) | v12 |
| Storage | Filesystem | - |

## Docker Configuration

### docker-compose.yml

```yaml
obs-loki:
  image: grafana/loki:2.9.0
  container_name: obs-loki
  restart: unless-stopped
  ports:
    - "3100:3100"
  volumes:
    - ./../loki/loki-config.yml:/etc/loki/local-config.yaml:ro
    - loki_data:/loki
  command: -config.file=/etc/loki/local-config.yaml
  networks:
    - observability_network
```

## Configuration

### loki-config.yml

**Location:** `loki/loki-config.yml`

The Loki configuration defines:
- Server settings (port, authentication)
- Storage settings (where to store log data)
- Schema configuration (how to organize data)
- Rate limits and retention

```yaml
# =============================================================================
# AUTHENTICATION
# =============================================================================
auth_enabled: false                      # Disable authentication for local development

# =============================================================================
# SERVER SETTINGS
# =============================================================================
server:
  http_listen_port: 3100                 # HTTP API port

# =============================================================================
# COMMON SETTINGS
# =============================================================================
common:
  instance_addr: 127.0.0.1              # Instance address (localhost)
  path_prefix: /loki                     # Root directory for all Loki data
  storage:
    filesystem:
      chunks_directory: /loki/chunks     # Directory for compressed log data
      rules_directory: /loki/rules       # Directory for recording rules
  replication_factor: 1                  # 1 = single node (no replication)
  ring:
    kvstore:
      store: inmemory                    # Store ring info in memory

# =============================================================================
# SCHEMA CONFIGURATION
# =============================================================================
schema_config:
  configs:
    - from: 2024-01-01                   # Start using this schema from this date
      store: tsdb                        # Use TSDB for storage
      object_store: filesystem           # Store objects on local filesystem
      schema: v12                        # Schema version (latest)
      index:
        prefix: index_                   # Prefix for index files
        period: 24h                      # Rotate index every 24 hours

# =============================================================================
# LIMITS CONFIGURATION
# =============================================================================
limits_config:
  retention_period: 30d                  # Keep logs for 30 days
  ingestion_rate_mb: 16                  # Max ingestion rate (MB/s)
  ingestion_burst_size_mb: 32            # Max burst size (MB)
```

See [loki/loki-config.yml](https://github.com/MdAshiqurRahmanZayed/django-observability/blob/main/loki/loki-config.yml) for full configuration with comments.

## Network Access

| Access | URL |
|--------|-----|
| External (host) | http://localhost:3100 |
| Internal (Docker) | http://obs-loki:3100 |

## Data Flow

### Log Push Flow

```
1. Promtail reads log file line
        │
        ▼
2. Parse JSON (if JSON formatted)
   Extract labels: app, level, logger
        │
        ▼
3. Send to Loki
   POST http://obs-loki:3100/loki/api/v1/push
        │
        ▼
4. Loki receives and stores:
   - Index: labels → chunk ID
   - Chunk: actual log lines
        │
        ▼
5. Available for querying
```

### Log Query Flow

```
1. Grafana sends query to Loki
   GET /loki/api/v1/query?query={app="django"}
        │
        ▼
2. Loki uses index to find matching chunks
        │
        ▼
3. Retrieve log lines from chunks
        │
        ▼
4. Return to Grafana for display
```

## Log Storage

Loki stores data differently than Elasticsearch:

| Aspect | Loki | Elasticsearch |
|--------|------|---------------|
| Index | Labels only | Full text + labels |
| Storage | Much smaller | Full text indexed |
| Query | LogQL | Lucene |
| Speed | Fast for labels | Fast for text search |

### Storage Structure

```
/loki/
├── chunks/          # Compressed log data
│   └── ...
├── index/           # Label index
│   └── ...
├── rules/           # Recording rules
└── wal/            # Write-ahead log
```

## Useful Commands

### Container Management

```bash
# Restart Loki
docker compose -f django_app/docker-compose.yml restart obs-loki

# View logs
docker logs -f obs-loki

# Access shell
docker exec -it obs-loki /bin/sh
```

### Push Logs (Testing)

```bash
# Push a test log
curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test","level":"info"},"values":[["'$(date +%s)'000000000","test message"]]}]}'
```

### Query Logs

```bash
# Query all logs for app=django (URL encoded)
curl -s 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'

# Query with level filter
curl -s 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22,level%3D%22ERROR%22%7D'

# Query range
curl -s 'http://localhost:3100/loki/api/v1/query_range?query=%7Bapp%3D%22django%22%7D&start=1773532800000000000&end=1773536400000000000&limit=100'
```

### Storage Inspection

```bash
# Check storage size
docker exec obs-loki du -sh /loki/

# List chunks
docker exec obs-loki ls -la /loki/chunks/
```

## Expected Output

### Push Response

```bash
$ curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test"},"values":[["1773536578000000000","hello"]]}]}'

# Response: (empty = success, HTTP 204)
```

### Query Response

```bash
$ curl -s 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22django%22%7D'

{
  "status": "success",
  "data": {
    "resultType": "streams",
    "result": [
      {
        "stream": {"app": "django", "level": "INFO"},
        "values": [
          ["1773536578000000000", "GET /todo/ 200"]
        ]
      }
    ]
  }
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/loki/api/v1/push` | POST | Push log entries |
| `/loki/api/v1/query` | GET | Instant query |
| `/loki/api/v1/query_range` | GET | Range query |
| `/loki/api/v1/label` | GET | List labels |
| `/loki/api/v1/label/{name}/values` | GET | Label values |
| `/ready` | GET | Health check |
| `/metrics` | GET | Prometheus metrics |

### Query Examples

| Query | Description |
|-------|-------------|
| `{app="django"}` | All Django logs |
| `{app="django",level="ERROR"}` | Django errors only |
| `{app="django"} \|= "POST"` | Logs containing "POST" |
| `{app="django"} \|~ "error.*failed"` | Regex match |
| `rate({app="django"}[5m])` | Logs per second |
| `count_over_time({app="django"}[5m])` | Count in 5min |

## Health Checks

```bash
# Health check
curl http://localhost:3100/ready

# Metrics
curl http://localhost:3100/metrics | head

# Check storage
docker exec obs-loki curl -s http://localhost:3100/loki/api/v1/index/stats
```

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| loki-config.yml | loki/loki-config.yml | Loki configuration |

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Promtail | Push to :3100 | Log ingestion |
| Grafana | Query :3100 | Log visualization |

## Troubleshooting

### Logs Not Appearing

```bash
# Check Promtail is running
docker ps | grep promtail

# Check Promtail logs
docker logs obs-promtail | tail -20

# Test push manually
curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test"},"values":[["'"$(date +%s)"'000000000","test"]]}]}'

# Query Loki
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22test%22%7D'
```

### High Storage Usage

```bash
# Check storage
docker exec obs-loki du -sh /loki/

# Check retention
docker exec obs-loki cat /etc/loki/local-config.yaml | grep retention
```

### Query Timeout

```bash
# Reduce query limit
curl 'http://localhost:3100/loki/api/v1/query?query={app="django"}&limit=100'
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-loki

# Stop
docker compose -f django_app/docker-compose.yml stop obs-loki

# Restart
docker compose -f django_app/docker-compose.yml restart obs-loki

# View logs
docker logs -f obs-loki
```

### URLs

| Service | URL |
|---------|-----|
| Loki API | http://localhost:3100 |
| Push | http://localhost:3100/loki/api/v1/push |
| Query | http://localhost:3100/loki/api/v1/query |
| Health | http://localhost:3100/ready |
| Metrics | http://localhost:3100/metrics |

### Key Ports

| Port | Service |
|------|---------|
| 3100 | Loki HTTP API |

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| retention_period | 30d | Log retention |
| ingestion_rate_mb | 16 | Max ingestion rate |
| schema v12 | 2024-01-01 | Index schema |

---

## Related Documentation

- [Promtail](./05-promtail.md) - Log shipping
- [Grafana](./03-grafana.md) - Log visualization
- [Django App](./01-django-app.md) - Log source
