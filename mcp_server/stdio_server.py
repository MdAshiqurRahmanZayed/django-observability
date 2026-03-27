"""
MCP Server for Django Observability Project - STDIO Transport
=============================================================
Stdio-based MCP server for backward compatibility with Claude Desktop.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .core import call_tool, get_tool_definitions

# ── App ───────────────────────────────────────────────────────────────────────

app = Server("django-observability")


# ── Tool Definitions ──────────────────────────────────────────────────────────


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Return all available MCP tools."""
    tools = []
    for tool_def in get_tool_definitions():
        tools.append(
            Tool(
                name=tool_def["name"],
                description=tool_def["description"],
                inputSchema=tool_def["inputSchema"],
            )
        )
    return tools


# ── Tool Implementation ──────────────────────────────────────────────────────


@app.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls from MCP client."""
    try:
        result = await call_tool(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [
            TextContent(
                type="text", text=f"❌ Error in tool '{name}': {type(e).__name__}: {e}"
            )
        ]


# ── Entry Point ───────────────────────────────────────────────────────────────


async def run_stdio():
    """Run stdio MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
