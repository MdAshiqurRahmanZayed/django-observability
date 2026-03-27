"""
MCP Server for Django Observability Project - HTTP Transport
============================================================
HTTP-based MCP server using FastAPI for remote access.
Supports both REST API and SSE (Server-Sent Events) transport.
"""

import asyncio
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from .core import ENV as _ENV
from .core import call_tool, get_tool_definitions

# ── Configuration ────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)

# Optional API key authentication
API_KEY = os.getenv("MCP_API_KEY", "") or _ENV.get("MCP_API_KEY", "")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verify_api_key(key: str = Security(api_key_header)) -> str | None:
    """Verify API key if configured."""
    if not API_KEY:
        return None  # No auth required if not configured
    if not key or key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return key


# ── Models ────────────────────────────────────────────────────────────────────


class MCPToolRequest(BaseModel):
    """Request model for MCP tool calls."""

    name: str = Field(..., description="Tool name to execute")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Tool arguments"
    )


class MCPToolResponse(BaseModel):
    """Response model for MCP tool calls."""

    content: list[dict[str, Any]] = Field(..., description="Response content")
    isError: bool = Field(default=False, description="Whether an error occurred")


class ToolInfo(BaseModel):
    """Tool definition model."""

    name: str
    description: str
    inputSchema: dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str = "1.0.0"
    transport: str = "http"


# ── SSE Session Management ──────────────────────────────────────────────────

# Store active SSE connections
sse_sessions: dict[str, asyncio.Queue] = {}


async def _handle_mcp_request(method: str, params: dict, session_id: str) -> dict:
    """Handle MCP JSON-RPC request and return response."""
    req_id = params.get("id", str(uuid.uuid4()))

    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "django-observability",
                        "version": "1.0.0",
                    },
                },
            }

        elif method == "notifications/initialized":
            return None  # No response needed for notifications

        elif method == "tools/list":
            tools = get_tool_definitions()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools},
            }

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})

            result = await call_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": result}],
                    "isError": False,
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    except Exception as e:
        logger.exception(f"Error handling MCP request: {method}")
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": f"Error: {e}"}],
                "isError": True,
            },
        }


# ── App Setup ─────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("MCP HTTP server starting...")
    yield
    logger.info("MCP HTTP server shutting down...")
    sse_sessions.clear()


app = FastAPI(
    title="Django Observability MCP Server",
    description="Model Context Protocol server for Django Observability project",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── SSE Endpoints (for OpenCode, Claude Desktop, etc.) ──────────────────────


@app.get("/sse", tags=["SSE"])
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP clients (OpenCode, Claude Desktop, etc.)."""

    async def event_generator():
        session_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue()
        sse_sessions[session_id] = queue

        # Send endpoint URL as first event
        endpoint_url = f"{request.base_url}messages/?session_id={session_id}"
        yield {"event": "endpoint", "data": str(endpoint_url)}

        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break

                try:
                    # Wait for messages with timeout
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield {"event": "message", "data": json.dumps(message)}
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield {"event": "ping", "data": ""}
        except asyncio.CancelledError:
            pass
        finally:
            sse_sessions.pop(session_id, None)

    return EventSourceResponse(event_generator())


@app.post("/messages/", tags=["SSE"])
async def messages_endpoint(request: Request):
    """Receive MCP JSON-RPC messages from SSE clients."""
    session_id = request.query_params.get("session_id", "")

    # Verify API key from header
    if API_KEY:
        key = request.headers.get(API_KEY_NAME, "")
        if not key or key != API_KEY:
            return JSONResponse(status_code=403, content={"error": "Invalid API key"})

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    method = body.get("method", "")
    params = body.get("params", {})

    # Handle the request
    response = await _handle_mcp_request(method, params, session_id)

    if response is None:
        # Notification, no response needed
        return JSONResponse(status_code=202, content={})

    # Send response back via SSE if session exists
    if session_id in sse_sessions:
        await sse_sessions[session_id].put(response)

    # Also return directly
    return JSONResponse(content=response)


# ── REST Endpoints (for curl, direct API calls) ─────────────────────────────


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.get("/tools", response_model=list[ToolInfo], tags=["Tools"])
async def list_tools(api_key: str | None = Security(verify_api_key)):
    """List all available MCP tools."""
    return [ToolInfo(**tool) for tool in get_tool_definitions()]


@app.post("/mcp/tools/{tool_name}", response_model=MCPToolResponse, tags=["MCP"])
async def execute_tool(
    tool_name: str,
    request: MCPToolRequest | None = None,
    api_key: str | None = Security(verify_api_key),
):
    """Execute an MCP tool by name."""
    if request is None:
        request = MCPToolRequest(name=tool_name, arguments={})
    elif request.name != tool_name:
        request.name = tool_name

    tool_names = [t["name"] for t in get_tool_definitions()]
    if tool_name not in tool_names:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {', '.join(tool_names)}",
        )

    try:
        result = await call_tool(tool_name, request.arguments)
        return MCPToolResponse(
            content=[{"type": "text", "text": result}], isError=False
        )
    except Exception as e:
        logger.exception(f"Error executing tool '{tool_name}'")
        return MCPToolResponse(
            content=[{"type": "text", "text": f"❌ Error: {type(e).__name__}: {e}"}],
            isError=True,
        )


@app.post("/mcp/invoke", response_model=MCPToolResponse, tags=["MCP"])
async def invoke_tool(
    request: MCPToolRequest,
    api_key: str | None = Security(verify_api_key),
):
    """Generic MCP tool invocation endpoint."""
    tool_name = request.name

    tool_names = [t["name"] for t in get_tool_definitions()]
    if tool_name not in tool_names:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {', '.join(tool_names)}",
        )

    try:
        result = await call_tool(tool_name, request.arguments)
        return MCPToolResponse(
            content=[{"type": "text", "text": result}], isError=False
        )
    except Exception as e:
        logger.exception(f"Error executing tool '{tool_name}'")
        return MCPToolResponse(
            content=[{"type": "text", "text": f"❌ Error: {type(e).__name__}: {e}"}],
            isError=True,
        )


# ── JSON-RPC Endpoint (for SSE-based MCP clients) ──────────────────────────


@app.post("/", tags=["MCP JSON-RPC"])
async def jsonrpc_endpoint(request: Request):
    """JSON-RPC endpoint for MCP protocol (StreamableHTTP transport)."""
    # Verify API key
    if API_KEY:
        key = request.headers.get(API_KEY_NAME, "")
        if not key or key != API_KEY:
            return JSONResponse(status_code=403, content={"error": "Invalid API key"})

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    method = body.get("method", "")
    params = body.get("params", {})
    req_id = body.get("id")

    # Handle session ID (StreamableHTTP transport)
    session_id = request.headers.get("Mcp-Session-Id", str(uuid.uuid4()))

    response = await _handle_mcp_request(method, {"id": req_id, **params}, session_id)

    if response is None:
        return JSONResponse(status_code=202, content={})

    # Return with session ID header for StreamableHTTP
    return JSONResponse(
        content=response,
        headers={"Mcp-Session-Id": session_id},
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with server information."""
    return {
        "server": "Django Observability MCP Server",
        "version": "1.0.0",
        "transport": ["http", "sse"],
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages/",
            "jsonrpc": "/",
            "health": "/health",
            "tools": "/tools",
            "invoke": "/mcp/invoke",
            "execute": "/mcp/tools/{tool_name}",
            "docs": "/docs",
        },
    }


# ── Entry Point ───────────────────────────────────────────────────────────────


def run_http():
    """Run HTTP MCP server."""
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info")

    logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))

    logger.info(f"Starting MCP HTTP server on {host}:{port}")
    uvicorn.run(
        "mcp_server.http_server:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv("RELOAD", "false").lower() == "true",
    )
