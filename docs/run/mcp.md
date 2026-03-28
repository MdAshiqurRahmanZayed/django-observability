# Run MCP Server

Step-by-step guide to run the MCP Server for AI integration.

---

## What is MCP Server?

The MCP (Model Context Protocol) Server provides AI assistants (like Claude) with tools to:

- Read/write project files
- Full CRUD on PostgreSQL (Todo app)
- Query Prometheus metrics
- Get Grafana dashboards/alerts
- Check service health

---

## Prerequisites

- All other services running (Django, PostgreSQL, Prometheus, Grafana, Loki)

---

## Start

### Option 1: Start All (Recommended)

```bash
docker compose -f django_app/docker-compose.yml up -d
```

The MCP Server will be available at http://localhost:8000

### Option 2: Start MCP Server Only

```bash
docker compose -f django_app/docker-compose.yml up -d obs-mcp-server
```

---

## Verify

```bash
# Check container
docker ps | grep obs-mcp-server

# Test health
curl http://localhost:8000/health
```

???+ success "Expected Output"
    ```json
    {"status": "healthy"}
    ```

---

## Access

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | MCP Server API |
| http://localhost:8000/health | Health check |
| http://localhost:8000/tools | List available tools |

---

## Available Tools

### Filesystem

| Tool | Description |
|------|-------------|
| `read_file` | Read project file |
| `write_file` | Write project file |
| `list_directory` | List files/folders |
| `get_file_info` | Get file metadata |
| `run_shell_command` | Run shell command |

### Database (Read)

| Tool | Description |
|------|-------------|
| `get_todo_stats` | Todo statistics |
| `list_todos` | List todos |
| `get_todo` | Get single todo |
| `run_db_query` | Run SELECT query |

### Database (Write)

| Tool | Description |
|------|-------------|
| `create_todo` | Create new todo |
| `update_todo` | Update todo |
| `delete_todo` | Delete todo |
| `bulk_delete_todos` | Delete multiple todos |
| `mark_todo_complete` | Mark complete |
| `mark_todo_incomplete` | Mark incomplete |

### Prometheus

| Tool | Description |
|------|-------------|
| `get_server_resources` | CPU, memory, disk |
| `get_django_metrics` | Django HTTP metrics |
| `prometheus_query` | Custom PromQL query |

### Grafana

| Tool | Description |
|------|-------------|
| `get_grafana_dashboards` | List dashboards |
| `get_grafana_alerts` | List alerts |
| `get_grafana_datasources` | List datasources |

### Health

| Tool | Description |
|------|-------------|
| `check_service_health` | Check all services |
| `get_full_status` | Full status dashboard |

---

## Commands

### View Logs

```bash
docker logs -f obs-mcp-server
```

### Access Shell

```bash
docker exec -it obs-mcp-server /bin/sh
```

### Test Tools

```bash
# Check service health
curl -X POST http://localhost:8000/tool \
  -H "Content-Type: application/json" \
  -d '{"tool": "check_service_health", "arguments": {}}'

# Get todo stats
curl -X POST http://localhost:8000/tool \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_todo_stats", "arguments": {}}'

# Get server resources
curl -X POST http://localhost:8000/tool \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_server_resources", "arguments": {"minutes": 30}}'
```

### Restart

```bash
docker compose -f django_app/docker-compose.yml restart obs-mcp-server
```

---

## Configuration

### Environment Variables

From `django_app/.env`:

```bash
# Database (for MCP server to connect)
DB_NAME=todo_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=obs-postgres
DB_PORT=5432

# Grafana (for MCP server to query)
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin
```

---

## Integrating with Claude

### Claude Desktop Configuration

Add to your Claude config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "django-observability": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### Using MCP Tools

Once configured, Claude can use the tools:

```
@django-observability check_service_health
@django-observability get_todo_stats
@django-observability get_server_resources
```

---

## Troubleshooting

??? failure "MCP Server not responding"
    ```bash
    # Check container
    docker ps | grep obs-mcp-server

    # Check logs
    docker logs obs-mcp-server

    # Test health
    curl http://localhost:8000/health
    ```

??? failure "Database connection failed"
    ```bash
    # Check PostgreSQL is running
    docker ps | grep obs-postgres

    # Test connection from MCP server
    docker exec obs-mcp-server python -c "import psycopg2; psycopg2.connect(host='obs-postgres', user='postgres', password='postgres', dbname='todo_db')"
    ```

??? failure "Prometheus metrics not available"
    ```bash
    # Check Prometheus is running
    curl http://localhost:9090/-/healthy

    # Test from MCP server
    docker exec obs-mcp-server wget -qO- http://obs-prometheus:9090/-/healthy
    ```

---

## Stop

```bash
docker compose -f django_app/docker-compose.yml stop obs-mcp-server
```
