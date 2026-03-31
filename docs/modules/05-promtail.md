# Promtail

## Overview

Promtail is an agent that ships logs from local files to Loki. It's the log collector in this observability stack, tailing log files from Django and sending them to Loki for storage and querying.

## Description

Promtail is a lightweight agent that:
- Tails log files (continuously reads new lines)
- Parses and processes log lines
- Adds labels for easy querying
- Pushes logs to Loki via HTTP

In this stack, Promtail:
- Tails Django application logs
- Tails Gunicorn access and error logs
- Parses JSON log format
- Extracts labels (level, logger)
- Pushes to Loki automatically

> **Note**: You don't need to manually push logs! Promtail handles everything automatically.

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROMTAIL IN STACK                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐     TAILS FILES      ┌──────────────┐                    │
│   │  Django      │ ────────────────────▶│   Promtail   │                    │
│   │  Logs        │   /app/logs/         │    :9080     │                    │
│   └──────────────┘                      └──────┬───────┘                    │
│                                                │                            │
│                                                │ PUSH                       │
│                                                ▼                            │
│                                          ┌──────────────┐                   │
│                                          │     Loki     │                   │
│                                          │    :3100     │                   │
│                                          └──────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Log Shipper | Promtail | 2.9.0 |
| Pipeline | YAML config | - |

## Docker Configuration

### docker-compose.yml

```yaml
obs-promtail:
  image: grafana/promtail:2.9.0
  container_name: obs-promtail
  restart: unless-stopped
  volumes:
    - ./../promtail/promtail-config.yml:/etc/promtail/config.yml:ro
    - logs_volume:/var/log/django:ro
  command: -config.file=/etc/promtail/config.yml
  depends_on:
    - obs-loki
  networks:
    - observability_network
```

## Configuration

### promtail-config.yml

**Location:** `promtail/promtail-config.yml`

The Promtail configuration defines:
- Server settings (port)
- Position tracking (remembers where it left off)
- Where to send logs (Loki endpoint)
- What files to watch and how to parse them

```yaml
# =============================================================================
# SERVER SETTINGS
# =============================================================================
server:
  http_listen_port: 9080                 # Port for metrics endpoint
  grpc_listen_port: 0                    # Disable gRPC (not needed)

# =============================================================================
# POSITION TRACKING
# =============================================================================
positions:
  filename: /tmp/positions.yaml          # File to store read positions

# =============================================================================
# CLIENT CONFIGURATION
# =============================================================================
clients:
  - url: http://obs-loki:3100/loki/api/v1/push  # Loki push endpoint

# =============================================================================
# SCRAPE CONFIGURATIONS
# =============================================================================
scrape_configs:

  # ===========================================================================
  # JOB 1: Django Application Logs (JSON Format)
  # ===========================================================================
  - job_name: django                     # Job name
    static_configs:
      - targets:
          - localhost                    # Required but ignored for file watching
        labels:
          app: django                    # Label: app=django
          env: dev                       # Label: env=dev
          __path__: /var/log/django/django.log  # File to watch
    pipeline_stages:
      - json:                            # Parse as JSON
          expressions:
            level: levelname             # Extract "levelname" → "level" label
            logger: name                 # Extract "name" → "logger" label
            message: message             # Extract "message" → log line
      - labels:                          # Convert to Loki labels
          level:
          logger:

  # ===========================================================================
  # JOB 2: Gunicorn Access Logs
  # ===========================================================================
  - job_name: gunicorn_access
    static_configs:
      - targets:
          - localhost
        labels:
          app: django
          log_type: access
          env: dev
          __path__: /var/log/django/access.log

  # ===========================================================================
  # JOB 3: Gunicorn Error Logs
  # ===========================================================================
  - job_name: gunicorn_error
    static_configs:
      - targets:
          - localhost
        labels:
          app: django
          log_type: error
          level: ERROR
          env: dev
          __path__: /var/log/django/error.log
```

See [promtail/promtail-config.yml](https://github.com/MdAshiqurRahmanZayed/django-observability/blob/main/promtail/promtail-config.yml) for full configuration with comments.

## Network Access

| Access | URL |
|--------|-----|
| Internal (Docker) | http://obs-promtail:9080 |

Note: Promtail doesn't expose ports externally - it's an agent that runs internally.

## How It Works

### File Tailing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PROMTAIL WORKING PROCESS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. STARTUP                                                                │
│   ───────────                                                               │
│   Promtail reads config file                                                │
│   Identifies which files to tail                                            │
│   Reads positions.yaml to know where to start                               │
│                                                                             │
│   2. TAILING                                                                │
│   ──────────                                                                │
│   Continuously watch log files (like `tail -f`)                             │
│   Detect new lines appended                                                 │
│                                                                             │
│   3. PIPELINE                                                               │
│   ───────────                                                               │
│   For each new line:                                                        │
│   - Parse as JSON (if configured)                                           │
│   - Extract fields: level, logger, message                                  │
│   - Convert fields to labels                                                │
│                                                                             │
│   4. PUSH TO LOKI                                                           │
│   ─────────────                                                             │
│   Batch log lines                                                           │
│   POST to http://obs-loki:3100/loki/api/v1/push                             │
│                                                                             │
│   5. SAVE POSITION                                                          │
│   ───────────────                                                           │
│   Store file offset in /tmp/positions.yaml                                  │
│   (survives restarts)                                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Stages

| Stage | Purpose |
|-------|---------|
| `json` | Parse JSON log lines |
| `labels` | Extract JSON fields as labels |
| `regex` | Extract using regex |
| `timestamp` | Parse timestamp |
| `output` | Set log line content |

## Scrape Jobs

| Job | File | Labels |
|-----|------|--------|
| django | /var/log/django/django.log | app=django, env=dev |
| gunicorn_access | /var/log/django/access.log | app=django, log_type=access, env=dev |
| gunicorn_error | /var/log/django/error.log | app=django, log_type=error, level=ERROR, env=dev |

## Useful Commands

### Container Management

```bash
# Restart Promtail
docker compose -f django_app/docker-compose.yml restart obs-promtail

# View logs
docker logs -f obs-promtail

# Access shell
docker exec -it obs-promtail /bin/sh
```

### Verify Tailing

```bash
# Check if Promtail is tailing files
docker logs obs-promtail | grep "Adding target"

# Expected output:
# level=info ts=... caller=filetargetmanager.go:361 msg="Adding target" key="/var/log/django/django.log:{app=\"django\", env=\"dev\"}"
```

### Test Configuration

```bash
# Validate config file
docker exec obs-promtail promtail --validate-config

# Check client config
docker exec obs-promtail cat /etc/promtail/config.yml | grep -A5 "clients:"
```

### Check Positions

```bash
# View positions file
docker exec obs-promtail cat /tmp/positions.yaml
```

## Expected Output

### Promtail Logs

```bash
$ docker logs obs-promtail

level=info ts=... caller=promtail.go:133 msg="Reloading configuration file" md5sum=...
level=info ts=... caller=server.go:322 http=[::]:9080 grpc=[::]:33681 msg="server listening on addresses"
level=info ts=... caller=main.go:174 msg="Starting Promtail" version="(version=2.9.0, ...)"
level=info ts=... caller=filetargetmanager.go:361 msg="Adding target" key="/var/log/django/django.log:{app=\"django\", env=\"dev\"}"
level=info ts=... caller=filetarget.go:313 component=tailer msg="watching new directory" directory=/var/log/django
ts=... level=info msg="Seeked /var/log/django/django.log - &{Offset:0 Whence:0}"
level=info ts=... caller=tailer.go:145 component=tailer msg="tail routine: started" path=/var/log/django/django.log
```

### Targets Status

```bash
# Check targets via API
curl http://localhost:9080/targets
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/targets` | GET | Active scrape targets |
| `/metrics` | GET | Prometheus metrics |
| `/config` | GET | Current configuration |
| `/ready` | GET | Health check |

## Health Checks

```bash
# Check if Promtail is running
docker exec obs-promtail wget -qO- http://localhost:9080/ready

# Check targets
curl http://localhost:9080/targets | jq

# Verify tailing
docker logs obs-promtail | grep "tail routine: started"
```

## Configuration Files

| File | Path | Purpose |
|------|------|---------|
| promtail-config.yml | promtail/promtail-config.yml | Promtail configuration |

## Integration Points

| Service | Connection | Purpose |
|---------|------------|---------|
| Loki | Push to :3100 | Log storage |
| Django logs | Read from volume | Log source |

## Troubleshooting

### Logs Not Reaching Loki

```bash
# Check Promtail is running
docker ps | grep promtail

# Check Promtail logs
docker logs obs-promtail

# Verify Loki is running
docker logs obs-loki | head

# Test push manually
curl -X POST 'http://localhost:3100/loki/api/v1/push' \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"app":"test"},"values":[["'"$(date +%s)"'000000000","test"]]}]}'

# Query test logs
curl 'http://localhost:3100/loki/api/v1/query?query=%7Bapp%3D%22test%22%7D'
```

### File Not Being Tailed

```bash
# Check if log file exists in container
docker exec obs-promtail ls -la /var/log/django/

# Check Promtail target status
curl http://localhost:9080/targets | jq

# Verify volume mount
docker inspect obs-promtail | jq '.[0].Mounts'
```

### High Memory Usage

```bash
# Check resource usage
docker stats obs-promtail

# Check position file size
docker exec obs-promtail du -sh /tmp/positions.yaml
```

## Quick Reference

### Docker Commands

```bash
# Start
docker compose -f django_app/docker-compose.yml up -d obs-promtail

# Stop
docker compose -f django_app/docker-compose.yml stop obs-promtail

# Restart
docker compose -f django_app/docker-compose.yml restart obs-promtail

# View logs
docker logs -f obs-promtail
```

### Key Paths

| Path | Description |
|------|-------------|
| /etc/promtail/config.yml | Config file |
| /var/log/django/ | Log files |
| /tmp/positions.yaml | Position tracker |

### Configuration Options

| Option | Purpose |
|--------|---------|
| `__path__` | File path to tail |
| `pipeline_stages` | Log processing steps |
| `labels` | Static labels to add |

### How Log Push Works (Automatic)

```
You write logs:     logger.info("message")
        │
        ▼
Django writes:     /app/logs/django.log (JSON)
        │
        ▼
Promtail tails:    reads new lines automatically
        │
        ▼
Promtail parses:   extracts labels (level, logger)
        │
        ▼
Promtail pushes:   POST /loki/api/v1/push (automatic!)
        │
        ▼
Loki stores:       queryable in Grafana

YOU DON'T DO ANYTHING - PROMTAIL DOES IT ALL!
```

---

## Related Documentation

- [Loki](./04-loki.md) - Log storage
- [Grafana](./03-grafana.md) - Log visualization
- [Django App](./01-django-app.md) - Log source
