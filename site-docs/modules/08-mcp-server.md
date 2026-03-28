# MCP Server (Model Context Protocol)

## Overview

The MCP Server provides AI assistants (like Claude) with tools to interact with your observability stack. It enables file operations, database management, metrics queries, and service health checks through a standardized protocol.

## Description

This MCP Server is a custom implementation that bridges AI assistants with your Django observability stack. It provides:

- **File Operations** - Read/write/list project files
- **Database Operations** - Full CRUD on PostgreSQL (Todo app)
- **Metrics Queries** - Prometheus metrics for server resources
- **Grafana Integration** - Dashboards, alerts, datasources
- **Service Health** - Check all stack services
- **Shell Commands** - Run docker compose commands

## Purpose in Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       MCP SERVER IN STACK                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         AI Assistant (Claude)                               │
│                               │                                             │
│                               ▼                                             │
│                   ┌───────────────────────┐                                 │
│                   │    MCP Server         │                                 │
│                   │  (mcp_filesystem_     │                                 │
│                   │   server.py)          │                                 │
│                   └───────────┬───────────┘                                 │
│                               │                                             │
│         ┌─────────────────────┼─────────────────────┐                       │
│         │                     │                     │                       │
│         ▼                     ▼                     ▼                       │
│   ┌───────────┐        ┌───────────┐        ┌───────────┐                   │
│   │ Filesystem│        │ PostgreSQL│        │Prometheus │                   │
│   │  (files)  │        │  (todos)  │        │(metrics)  │                   │
│   └───────────┘        └───────────┘        └───────────┘                   │
│                                                                             │
│                    ┌──────────-─┐        ┌───────────┐                      │
│                    │  Grafana   │        │ Services  │                      │
│                    │(dashboards)│        │ (health)  │                      │
│                    └───────────-┘        └───────────┘                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Technology

| Component | Technology | Version |
|-----------|------------|---------|
| Protocol | MCP (Model Context Protocol) | - |
| Server | Python + mcp package | - |
| HTTP Client | httpx | - |
| DB Client | psycopg2 | - |

## File Location

```
django-observability/
└── mcp_filesystem_server.py   # MCP Server implementation
```

## Available Tools

### 1. Filesystem Operations

| Tool | Description |
|------|-------------|
| `read_file` | Read contents of a project file |
| `write_file` | Write content to a project file |
| `list_directory` | List files/folders in a directory |
| `get_file_info` | Get file metadata (size, modified) |
| `run_shell_command` | Run shell commands (docker compose, etc.) |

### 2. Database - Todo (Read)

| Tool | Description |
|------|-------------|
| `get_todo_stats` | Get todo statistics (total, completed, pending) |
| `list_todos` | List todos with optional filter (all/completed/pending) |
| `get_todo` | Get a single todo by ID |
| `run_db_query` | Run a read-only SELECT query |

### 3. Database - Todo (Write)

| Tool | Description |
|------|-------------|
| `create_todo` | Create a new todo |
| `update_todo` | Update todo title and/or completed status |
| `delete_todo` | Delete a todo by ID |
| `bulk_delete_todos` | Delete multiple todos by IDs |
| `mark_todo_complete` | Mark a todo as completed |
| `mark_todo_incomplete` | Mark a todo as pending |
| `run_db_write` | Run INSERT/UPDATE/DELETE query |

### 4. Prometheus/Metrics

| Tool | Description |
|------|-------------|
| `get_server_resources` | CPU, memory, disk usage (past 30 min) |
| `get_django_metrics` | Django HTTP metrics (request rate, error rate, latency) |
| `prometheus_query` | Run custom PromQL query |

### 5. Grafana

| Tool | Description |
|------|-------------|
| `get_grafana_dashboards` | List all Grafana dashboards |
| `get_grafana_alerts` | Get alert rules and states |
| `get_grafana_datasources` | List configured datasources |

### 6. Service Health

| Tool | Description |
|------|-------------|
| `check_service_health` | Check health of all stack services |
| `get_full_status` | One-shot: health + resources + metrics + todo stats |

## Configuration

### Environment Variables

The MCP Server reads from `django_app/.env`:

```bash
# Database
DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=obs-postgres
DB_PORT=5432

# Grafana
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin
```

### URLs (Hardcoded)

```python
PROMETHEUS_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3000"
DJANGO_URL = "http://localhost:9000"
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MCP SERVER WORKING PROCESS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. STARTUP                                                                │
│   ───────────                                                               │
│   MCP Server starts via stdio (not HTTP)                                    │
│   Reads .env for credentials                                                │
│                                                                             │
│   2. TOOL REGISTRATION                                                      │
│   ───────────────────                                                       │
│   Server registers all available tools with AI                              │
│   AI knows what tools are available                                         │
│                                                                             │
│   3. TOOL EXECUTION                                                         │
│   ───────────────                                                           │
│   AI calls a tool → MCP Server executes → Returns result                    │
│                                                                             │
│   4. DATABASE OPERATIONS                                                    │
│   ────────────────────                                                      │
│   Connects to PostgreSQL (todo_todo table)                                  │
│   Full CRUD support                                                         │
│                                                                             │
│   5. METRICS QUERIES                                                        │
│   ───────────────────                                                       │
│   Queries Prometheus API for metrics                                        │
│   Returns formatted results                                                 │
│                                                                             │
│   6. GRAFANA INTEGRATION                                                    │
│   ───────────────────────                                                   │
│   Lists dashboards, alerts, datasources                                     │
│   Returns formatted output                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Example Usage

#### Database Operations

```python
# Get todo statistics
get_todo_stats() → "📋 Todo Statistics\n  Total: 10\n  Completed: 5\n  Pending: 5"

# List all todos
list_todos(status="all", limit=20)

# Create a todo
create_todo(title="Learn MCP")

# Update a todo
update_todo(id=1, title="Updated title", completed=True)

# Delete a todo
delete_todo(id=1)
```

#### Prometheus Metrics

```python
# Get server resources (CPU, Memory, Disk)
get_server_resources(minutes=30)

# Get Django metrics
get_django_metrics(minutes=30)

# Custom PromQL query
prometheus_query(query="up")
```

#### Grafana

```python
# List dashboards
get_grafana_dashboards()

# Get alerts
get_grafana_alerts()

# Get datasources
get_grafana_datasources()
```

#### Service Health

```python
# Check all services
check_service_health()

# Get full status dashboard
get_full_status(minutes=30)
```

## Running the MCP Server

### Direct Execution

```bash
# Run the MCP server
python mcp_filesystem_server.py
```

### With Claude Desktop

Add to your Claude config (typically `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "django-observability": {
      "command": "python",
      "args": ["/path/to/mcp_filesystem_server.py"]
    }
  }
}
```

### Quick Test

```bash
# Test Prometheus connection
python3 -c "
import asyncio
import httpx
async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:9090/api/v1/query?query=up')
        print(r.json())
asyncio.run(test())
"

# Test Database connection
python3 -c "
import psycopg2
conn = psycopg2.connect(host='localhost', port=5439, user='postgres', password='postgres', dbname='todo_db')
print('Connected!')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM todo_todo')
print(f'Todos: {cur.fetchone()[0]}')
"
```

## Expected Output Examples

### check_service_health

```
🏥 Service Health ─────────────────────────────────────
  🟢 Django (app)         HTTP 200
  🟢 Prometheus           HTTP 200
  🟢 Grafana              HTTP 200
  🟢 Loki                 HTTP 200
  🟢 Alertmanager        HTTP 200
  🟢 Node Exporter       HTTP 200
  🟢 Nginx                HTTP 200
  🟢 PostgreSQL           Connected
```

### get_todo_stats

```
📋 Todo Statistics
──────────────────
  Total:     10
  Completed: 5
  Pending:   5

🕐 Latest 5 Todos:
  ✅ [1] Buy groceries (2026-03-15)
  🔲 [2] Learn Django (2026-03-14)
  ✅ [3] Fix bug #123 (2026-03-13)
```

### get_server_resources

```
🖥️  Server Resources (last 30 min)
────────────────────────────────────────
  CPU  — now: 25.3%   avg: 22.1%
  MEM  — now: 61.2%   avg: 58.5%
  DISK — used: 45.0%
```

### get_django_metrics

```
🌐 Django HTTP Metrics (last 30 min)
────────────────────────────────────────
  Total Requests : 1234
  Request Rate   : 0.686 req/s
  Error Rate (5xx): 0.0000 req/s
  Latency p95    : 45.2 ms
```

## Troubleshooting

### MCP Server Not Responding

```bash
# Test if script runs
python mcp_filesystem_server.py

# Check for missing dependencies
pip install mcp httpx psycopg2-binary
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection manually
python3 -c "import psycopg2; psycopg2.connect(host='localhost', port=5439, user='postgres', password='postgres', dbname='todo_db')"

# Check port mapping
docker ps | grep postgres
# Should show: 0.0.0.0:5439->5432/tcp
```

### Prometheus Metrics Not Available

```bash
# Check Prometheus is running
curl http://localhost:9090/-/healthy

# Check Django metrics endpoint
curl http://localhost:9000/metrics | head
```

### Grafana Auth Failed

```bash
# Check credentials in .env
cat django_app/.env | grep GF_ADMIN

# Test Grafana login
curl -u admin:admin http://localhost:3000/api/health
```

## Security Notes

- **Path Validation**: All file operations are restricted to project root
- **DB Access**: Only SELECT allowed via `run_db_query`, INSERT/UPDATE/DELETE via `run_db_write`
- **Credentials**: All credentials read from `.env` file
- **No Hardcoded Fallbacks**: Required env vars must be set

## Quick Reference

### MCP Tools Summary

| Category | Tools |
|----------|-------|
| Filesystem | read_file, write_file, list_directory, get_file_info, run_shell_command |
| DB Read | get_todo_stats, list_todos, get_todo, run_db_query |
| DB Write | create_todo, update_todo, delete_todo, bulk_delete_todos, mark_todo_complete, mark_todo_incomplete, run_db_write |
| Prometheus | get_server_resources, get_django_metrics, prometheus_query |
| Grafana | get_grafana_dashboards, get_grafana_alerts, get_grafana_datasources |
| Health | check_service_health, get_full_status |

### Environment Variables Required

| Variable | Description |
|----------|-------------|
| DB_USER | PostgreSQL username |
| DB_PASSWORD | PostgreSQL password |
| GF_ADMIN_USER | Grafana admin username |
| GF_ADMIN_PASSWORD | Grafana admin password |

---

## Related Documentation

- [Django App](./01-django-app.md) - Application with todo database
- [Prometheus](./02-prometheus.md) - Metrics source
- [Grafana](./03-grafana.md) - Visualization
