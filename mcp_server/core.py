"""
MCP Server for Django Observability Project - Core Tools
========================================================
Provides tools for:
  - Read/write project files
  - Full CRUD on PostgreSQL (Todo app DB)
  - Query Prometheus metrics (last 30 min resource usage)
  - Query Grafana (dashboards, datasources, alerts)
  - Check all service health statuses
  - Run shell commands (e.g. docker compose restart)
"""

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import httpx
import psycopg2
from psycopg2.extras import RealDictCursor

# ── Configuration ────────────────────────────────────────────────────────────

BASE_PATH = Path(__file__).resolve().parent.parent


def _load_env() -> dict:
    """Read .env from django_app — all credentials must be defined there."""
    env = {}
    env_file = BASE_PATH / "django_app" / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def _require(env: dict, key: str) -> str:
    """Return env value or raise — no hardcoded credential fallbacks."""
    value = env.get(key)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{key}' in django_app/.env"
        )
    return value


ENV = _load_env()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", ENV.get("DB_NAME", "todo_db")),
    "user": _require(ENV, "DB_USER"),
    "password": _require(ENV, "DB_PASSWORD"),
    "host": os.getenv("DB_HOST", ENV.get("DB_HOST", "localhost")),
    "port": int(os.getenv("DB_PORT", ENV.get("DB_PORT", "5439"))),
}

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL", ENV.get("PROMETHEUS_URL", "http://localhost:9090")
)
GRAFANA_URL = os.getenv("GRAFANA_URL", ENV.get("GRAFANA_URL", "http://localhost:3000"))
GRAFANA_USER = _require(ENV, "GF_ADMIN_USER")
GRAFANA_PASS = _require(ENV, "GF_ADMIN_PASSWORD")
DJANGO_URL = os.getenv("DJANGO_URL", ENV.get("DJANGO_URL", "http://localhost:9000"))

# ── Helpers ───────────────────────────────────────────────────────────────────


def _db_connect():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


async def _prometheus_query(query: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        r.raise_for_status()
        return r.json()


async def _prometheus_range(query: str, minutes: int = 30) -> dict:
    import time

    end = time.time()
    start = end - minutes * 60
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{PROMETHEUS_URL}/api/v1/query_range",
            params={"query": query, "start": start, "end": end, "step": "60"},
        )
        r.raise_for_status()
        return r.json()


async def _grafana_get(path: str) -> dict:
    async with httpx.AsyncClient(
        timeout=10, auth=(GRAFANA_USER, GRAFANA_PASS)
    ) as client:
        r = await client.get(f"{GRAFANA_URL}{path}")
        r.raise_for_status()
        return r.json()


def _fmt(obj) -> str:
    return json.dumps(obj, indent=2, default=str)


def _val(r):
    try:
        return float(r["data"]["result"][0]["value"][1])
    except Exception:
        return None


def _pct(v):
    return f"{v:.1f}%" if v is not None else "N/A"


# ── Tool Definitions ──────────────────────────────────────────────────────────


def get_tool_definitions() -> list[dict]:
    """Return all tool definitions as a list of dicts for reuse."""
    return [
        # ── Filesystem ──
        {
            "name": "read_file",
            "description": "Read contents of a project file (path relative to project root)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root",
                    }
                },
                "required": ["path"],
            },
        },
        {
            "name": "write_file",
            "description": "Write content to a project file, creating it or overwriting it (path relative to project root)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full file content to write",
                    },
                },
                "required": ["path", "content"],
            },
        },
        {
            "name": "list_directory",
            "description": "List files/folders in a project directory",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root (use '.' for root)",
                    }
                },
                "required": ["path"],
            },
        },
        {
            "name": "get_file_info",
            "description": "Get metadata (size, modified time) for a project file",
            "inputSchema": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
        {
            "name": "run_shell_command",
            "description": "Run a shell command inside the django_app directory (e.g. docker compose restart django). Cwd is always django_app/.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to run",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 60)",
                    },
                },
                "required": ["command"],
            },
        },
        # ── Django DB / Todo — READ ──
        {
            "name": "get_todo_stats",
            "description": "Get Todo statistics from the PostgreSQL database: total, completed, pending counts and the latest todos",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "list_todos",
            "description": "List todos from the database with optional filter",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "completed", "pending"],
                        "description": "Filter by status (default: all)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max rows to return (default 20)",
                    },
                },
            },
        },
        {
            "name": "get_todo",
            "description": "Get a single Todo item by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the todo to retrieve",
                    },
                },
                "required": ["id"],
            },
        },
        {
            "name": "run_db_query",
            "description": "Run a read-only SQL SELECT query against the PostgreSQL database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SELECT SQL query to execute",
                    }
                },
                "required": ["sql"],
            },
        },
        # ── Django DB / Todo — WRITE ──
        {
            "name": "create_todo",
            "description": "Create a new Todo item in the database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the new todo"},
                },
                "required": ["title"],
            },
        },
        {
            "name": "update_todo",
            "description": "Update a Todo item's title and/or completed status by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the todo to update",
                    },
                    "title": {"type": "string", "description": "New title (optional)"},
                    "completed": {
                        "type": "boolean",
                        "description": "Mark as completed or not (optional)",
                    },
                },
                "required": ["id"],
            },
        },
        {
            "name": "delete_todo",
            "description": "Delete a Todo item by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the todo to delete",
                    },
                },
                "required": ["id"],
            },
        },
        {
            "name": "bulk_delete_todos",
            "description": "Delete multiple Todo items by a list of IDs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of todo IDs to delete",
                    },
                },
                "required": ["ids"],
            },
        },
        {
            "name": "mark_todo_complete",
            "description": "Mark a Todo item as completed by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the todo to mark complete",
                    },
                },
                "required": ["id"],
            },
        },
        {
            "name": "mark_todo_incomplete",
            "description": "Mark a Todo item as incomplete (pending) by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "ID of the todo to mark incomplete",
                    },
                },
                "required": ["id"],
            },
        },
        {
            "name": "run_db_write",
            "description": "Run a raw INSERT, UPDATE, or DELETE SQL query against the PostgreSQL database",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query (INSERT / UPDATE / DELETE)",
                    },
                    "params": {
                        "type": "array",
                        "items": {},
                        "description": "Optional list of positional query parameters",
                    },
                },
                "required": ["sql"],
            },
        },
        # ── Prometheus / Metrics ──
        {
            "name": "get_server_resources",
            "description": "Get CPU usage, memory usage, and disk usage from the past 30 minutes via Prometheus",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": "Lookback window in minutes (default 30)",
                    }
                },
            },
        },
        {
            "name": "get_django_metrics",
            "description": "Get Django HTTP request metrics from the past 30 minutes (request rate, error rate, response time)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": "Lookback window in minutes (default 30)",
                    }
                },
            },
        },
        {
            "name": "prometheus_query",
            "description": "Run a custom PromQL query against Prometheus",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "PromQL query string"}
                },
                "required": ["query"],
            },
        },
        # ── Grafana ──
        {
            "name": "get_grafana_dashboards",
            "description": "List all Grafana dashboards",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_grafana_alerts",
            "description": "Get current Grafana alert rules and their states",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_grafana_datasources",
            "description": "List all configured Grafana datasources",
            "inputSchema": {"type": "object", "properties": {}},
        },
        # ── Service Health ──
        {
            "name": "check_service_health",
            "description": "Check health/reachability of all stack services: Django, Prometheus, Grafana, Loki, Alertmanager, Node Exporter, Postgres",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_full_status",
            "description": "One-shot dashboard: service health + server resources (CPU/MEM/DISK) + Django metrics + Todo stats for the past 30 minutes",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": "Lookback window in minutes (default 30)",
                    }
                },
            },
        },
    ]


# ── Tool Implementations ──────────────────────────────────────────────────────


async def call_tool(name: str, arguments: dict) -> str:
    """Dispatch tool call and return result string."""
    return await _dispatch(name, arguments)


async def _dispatch(name: str, args: dict) -> str:
    # ── Filesystem ────────────────────────────────────────────────────────────
    if name == "read_file":
        path = BASE_PATH / args["path"]
        if not str(path.resolve()).startswith(str(BASE_PATH)):
            return "Access denied: path outside project"
        return path.read_text()

    if name == "write_file":
        path = (BASE_PATH / args["path"]).resolve()
        if not str(path).startswith(str(BASE_PATH)):
            return "Access denied: path outside project"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args["content"])
        return (
            f"✅ Written {path.relative_to(BASE_PATH)} ({len(args['content'])} bytes)"
        )

    if name == "list_directory":
        path = BASE_PATH / args.get("path", ".")
        if not str(path.resolve()).startswith(str(BASE_PATH)):
            return "Access denied"
        items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        return "\n".join(f"{'d' if i.is_dir() else 'f'} {i.name}" for i in items)

    if name == "get_file_info":
        path = BASE_PATH / args["path"]
        if not str(path.resolve()).startswith(str(BASE_PATH)):
            return "Access denied"
        s = path.stat()
        return (
            f"Path:     {path}\n"
            f"Size:     {s.st_size:,} bytes\n"
            f"Modified: {datetime.fromtimestamp(s.st_mtime, tz=timezone.utc).isoformat()}\n"
            f"Type:     {'directory' if path.is_dir() else 'file'}"
        )

    if name == "run_shell_command":
        command = args["command"]
        timeout = args.get("timeout", 60)
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(BASE_PATH / "django_app"),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        lines = [f"$ {command}", f"exit code: {result.returncode}"]
        if out:
            lines += ["── stdout ──", out]
        if err:
            lines += ["── stderr ──", err]
        return "\n".join(lines)

    # ── DB / Todo — READ ──────────────────────────────────────────────────────
    if name == "get_todo_stats":
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total FROM todo_todo")
                total = cur.fetchone()["total"]
                cur.execute(
                    "SELECT COUNT(*) AS n FROM todo_todo WHERE completed = TRUE"
                )
                completed = cur.fetchone()["n"]
                cur.execute(
                    "SELECT COUNT(*) AS n FROM todo_todo WHERE completed = FALSE"
                )
                pending = cur.fetchone()["n"]
                cur.execute(
                    "SELECT id, title, completed, created_at FROM todo_todo ORDER BY created_at DESC LIMIT 5"
                )
                latest = cur.fetchall()
        conn.close()
        lines = [
            "📋 Todo Statistics",
            "──────────────────",
            f"  Total:     {total}",
            f"  Completed: {completed}",
            f"  Pending:   {pending}",
            "",
            "🕐 Latest 5 Todos:",
        ]
        for t in latest:
            status = "✅" if t["completed"] else "🔲"
            lines.append(
                f"  {status} [{t['id']}] {t['title']} ({t['created_at'].date()})"
            )
        return "\n".join(lines)

    if name == "list_todos":
        status = args.get("status", "all")
        limit = args.get("limit", 20)
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                if status == "completed":
                    cur.execute(
                        "SELECT id, title, completed, created_at FROM todo_todo WHERE completed=TRUE ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                elif status == "pending":
                    cur.execute(
                        "SELECT id, title, completed, created_at FROM todo_todo WHERE completed=FALSE ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                else:
                    cur.execute(
                        "SELECT id, title, completed, created_at FROM todo_todo ORDER BY created_at DESC LIMIT %s",
                        (limit,),
                    )
                rows = cur.fetchall()
        conn.close()
        if not rows:
            return "No todos found."
        lines = [f"Showing {len(rows)} todo(s) [{status}]:", ""]
        for r in rows:
            icon = "✅" if r["completed"] else "🔲"
            lines.append(
                f"  {icon} [{r['id']}] {r['title']}  —  {r['created_at'].date()}"
            )
        return "\n".join(lines)

    if name == "get_todo":
        todo_id = args["id"]
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, title, completed, created_at FROM todo_todo WHERE id = %s",
                    (todo_id,),
                )
                row = cur.fetchone()
        conn.close()
        if not row:
            return f"❌ No todo found with id {todo_id}."
        icon = "✅" if row["completed"] else "🔲"
        return (
            f"Todo [{row['id']}]\n"
            f"  Title:     {row['title']}\n"
            f"  Status:    {icon} {'Completed' if row['completed'] else 'Pending'}\n"
            f"  Created:   {row['created_at'].date()}"
        )

    if name == "run_db_query":
        sql = args["sql"].strip()
        if not sql.lower().startswith("select"):
            return "❌ Only SELECT queries are allowed. Use run_db_write for INSERT/UPDATE/DELETE."
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchmany(100)
        conn.close()
        if not rows:
            return "Query returned no rows."
        keys = list(rows[0].keys())
        lines = [" | ".join(keys), "-" * 60]
        for r in rows:
            lines.append(" | ".join(str(r[k]) for k in keys))
        return "\n".join(lines)

    # ── DB / Todo — CREATE ────────────────────────────────────────────────────
    if name == "create_todo":
        title = args["title"].strip()
        if not title:
            return "❌ Title cannot be empty."
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO todo_todo (title, completed, created_at) VALUES (%s, FALSE, NOW()) RETURNING id, title, created_at",
                    (title,),
                )
                row = cur.fetchone()
        conn.close()
        return f'✅ Created todo [{row["id"]}] "{row["title"]}" on {row["created_at"].date()}'

    # ── DB / Todo — UPDATE ────────────────────────────────────────────────────
    if name == "update_todo":
        todo_id = args["id"]
        title = args.get("title")
        completed = args.get("completed")

        if title is None and completed is None:
            return "❌ Provide at least one of: title, completed."

        fields, values = [], []
        if title is not None:
            fields.append("title = %s")
            values.append(title.strip())
        if completed is not None:
            fields.append("completed = %s")
            values.append(completed)
        values.append(todo_id)

        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE todo_todo SET {', '.join(fields)} WHERE id = %s RETURNING id, title, completed",
                    values,
                )
                row = cur.fetchone()
        conn.close()
        if not row:
            return f"❌ No todo found with id {todo_id}."
        icon = "✅" if row["completed"] else "🔲"
        return f'✏️  Updated [{row["id"]}] "{row["title"]}"  {icon}'

    if name == "mark_todo_complete":
        todo_id = args["id"]
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE todo_todo SET completed = TRUE WHERE id = %s RETURNING id, title",
                    (todo_id,),
                )
                row = cur.fetchone()
        conn.close()
        if not row:
            return f"❌ No todo found with id {todo_id}."
        return f'✅ Marked complete: [{row["id"]}] "{row["title"]}"'

    if name == "mark_todo_incomplete":
        todo_id = args["id"]
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE todo_todo SET completed = FALSE WHERE id = %s RETURNING id, title",
                    (todo_id,),
                )
                row = cur.fetchone()
        conn.close()
        if not row:
            return f"❌ No todo found with id {todo_id}."
        return f'🔲 Marked incomplete: [{row["id"]}] "{row["title"]}"'

    # ── DB / Todo — DELETE ────────────────────────────────────────────────────
    if name == "delete_todo":
        todo_id = args["id"]
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM todo_todo WHERE id = %s RETURNING id, title",
                    (todo_id,),
                )
                row = cur.fetchone()
        conn.close()
        if not row:
            return f"❌ No todo found with id {todo_id}."
        return f'🗑️  Deleted todo [{row["id"]}] "{row["title"]}"'

    if name == "bulk_delete_todos":
        ids = args["ids"]
        if not ids:
            return "❌ No IDs provided."
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM todo_todo WHERE id = ANY(%s) RETURNING id, title",
                    (ids,),
                )
                rows = cur.fetchall()
        conn.close()
        if not rows:
            return f"❌ No todos found for IDs: {ids}"
        deleted = ", ".join(f'[{r["id"]}] "{r["title"]}"' for r in rows)
        return f"🗑️  Deleted {len(rows)} todo(s): {deleted}"

    # ── Raw DB Write ──────────────────────────────────────────────────────────
    if name == "run_db_write":
        sql = args["sql"].strip()
        params = args.get("params", [])
        lower = sql.lower()
        if not any(lower.startswith(kw) for kw in ("insert", "update", "delete")):
            return "❌ Only INSERT, UPDATE, DELETE are allowed. Use run_db_query for SELECT."
        conn = _db_connect()
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or None)
                affected = cur.rowcount
        conn.close()
        return f"✅ Query executed successfully. Rows affected: {affected}"

    # ── Prometheus ────────────────────────────────────────────────────────────
    if name == "get_server_resources":
        minutes = args.get("minutes", 30)

        cpu_r = await _prometheus_query(
            '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
        )
        mem_r = await _prometheus_query(
            "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
        )
        disk_r = await _prometheus_query(
            '(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100'
        )
        cpu_avg = await _prometheus_query(
            f'avg_over_time((100 - (avg(rate(node_cpu_seconds_total{{mode="idle"}}[5m])) * 100))[{minutes}m:])'
        )
        mem_avg = await _prometheus_query(
            f"avg_over_time(((1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100)[{minutes}m:])"
        )

        return (
            f"🖥️  Server Resources (last {minutes} min)\n"
            f"{'─' * 40}\n"
            f"  CPU  — now: {_pct(_val(cpu_r))}   avg: {_pct(_val(cpu_avg))}\n"
            f"  MEM  — now: {_pct(_val(mem_r))}   avg: {_pct(_val(mem_avg))}\n"
            f"  DISK — used: {_pct(_val(disk_r))}\n"
        )

    if name == "get_django_metrics":
        minutes = args.get("minutes", 30)
        window = f"{minutes}m"

        req_rate = await _prometheus_query(
            f"sum(rate(django_http_requests_total_by_method_total[{window}]))"
        )
        err_rate = await _prometheus_query(
            f'sum(rate(django_http_responses_total_by_status_total{{status=~"5.."}}[{window}]))'
        )
        p95 = await _prometheus_query(
            f"histogram_quantile(0.95, sum(rate(django_http_responses_latency_seconds_bucket[{window}])) by (le))"
        )
        total_req = await _prometheus_query(
            f"sum(increase(django_http_requests_total_by_method_total[{window}]))"
        )

        rps = _val(req_rate)
        erps = _val(err_rate)
        lat_p95 = _val(p95)
        tot = _val(total_req)

        lines = [
            f"🌐 Django HTTP Metrics (last {minutes} min)",
            "─" * 40,
            f"  Total Requests : {int(tot) if tot is not None else 'N/A'}",
            f"  Request Rate   : {f'{rps:.3f} req/s' if rps is not None else 'N/A'}",
            f"  Error Rate (5xx): {f'{erps:.4f} req/s' if erps is not None else 'N/A'}",
            f"  Latency p95    : {f'{lat_p95 * 1000:.1f} ms' if lat_p95 is not None else 'N/A'}",
        ]
        return "\n".join(lines)

    if name == "prometheus_query":
        data = await _prometheus_query(args["query"])
        return _fmt(data)

    # ── Grafana ───────────────────────────────────────────────────────────────
    if name == "get_grafana_dashboards":
        data = await _grafana_get("/api/search?type=dash-db")
        if not data:
            return "No dashboards found."
        lines = ["📊 Grafana Dashboards", "─" * 40]
        for d in data:
            lines.append(f"  [{d.get('id')}] {d.get('title')}  —  {d.get('url')}")
        return "\n".join(lines)

    if name == "get_grafana_alerts":
        try:
            data = await _grafana_get("/api/v1/provisioning/alert-rules")
        except Exception:
            data = await _grafana_get("/api/alerts")
        lines = ["🔔 Grafana Alert Rules", "─" * 40]
        if isinstance(data, list):
            for a in data:
                name_ = a.get("title") or a.get("name", "unknown")
                state = a.get("state", a.get("status", "unknown"))
                lines.append(f"  {name_}  →  {state}")
        else:
            lines.append(_fmt(data))
        return "\n".join(lines)

    if name == "get_grafana_datasources":
        data = await _grafana_get("/api/datasources")
        lines = ["🗄️  Grafana Datasources", "─" * 40]
        for ds in data:
            lines.append(
                f"  [{ds.get('id')}] {ds.get('name')}  ({ds.get('type')})  →  {ds.get('url')}"
            )
        return "\n".join(lines)

    # ── Health Check ──────────────────────────────────────────────────────────
    if name == "check_service_health":
        services = {
            "Django (app)": ("http", f"{DJANGO_URL}/metrics"),
            "Prometheus": ("http", f"{PROMETHEUS_URL}/-/healthy"),
            "Grafana": ("http", f"{GRAFANA_URL}/api/health"),
            "Loki": ("http", "http://localhost:3100/ready"),
            "Alertmanager": ("http", "http://localhost:9093/-/healthy"),
            "Node Exporter": ("http", "http://localhost:9100/metrics"),
            "Nginx": ("http", "http://localhost:80/"),
        }
        lines = ["🏥 Service Health", "─" * 40]
        async with httpx.AsyncClient(timeout=5) as client:
            for svc, (_, url) in services.items():
                try:
                    r = await client.get(url)
                    icon = "🟢" if r.status_code < 400 else "🟡"
                    lines.append(f"  {icon} {svc:<22} HTTP {r.status_code}")
                except Exception as e:
                    lines.append(f"  🔴 {svc:<22} UNREACHABLE ({type(e).__name__})")

        try:
            conn = _db_connect()
            conn.close()
            lines.append(f"  🟢 {'PostgreSQL':<22} Connected")
        except Exception as e:
            lines.append(f"  🔴 {'PostgreSQL':<22} FAILED ({e})")

        return "\n".join(lines)

    # ── Full Status Dashboard ─────────────────────────────────────────────────
    if name == "get_full_status":
        minutes = args.get("minutes", 30)
        parts = []

        parts.append(await _dispatch("check_service_health", {}))
        parts.append("")
        parts.append(await _dispatch("get_server_resources", {"minutes": minutes}))
        parts.append("")
        parts.append(await _dispatch("get_django_metrics", {"minutes": minutes}))
        parts.append("")
        try:
            parts.append(await _dispatch("get_todo_stats", {}))
        except Exception as e:
            parts.append(f"📋 Todo Stats: unavailable ({e})")

        return "\n".join(parts)

    return f"Unknown tool: {name}"
