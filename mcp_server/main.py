"""
MCP Server for Django Observability Project - Main Entry Point
==============================================================
Supports multiple transport modes:
  - stdio: Standard I/O (default, for Claude Desktop)
  - http: HTTP/REST API (for remote access)
  - both: Run both transports concurrently
"""

import asyncio
import logging
import os
import sys

logger = logging.getLogger(__name__)


def setup_logging():
    """Configure logging based on environment."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


async def run_both_transports():
    """Run both stdio and HTTP transports concurrently."""
    from .stdio_server import run_stdio

    # Start HTTP server as a background task
    http_task = asyncio.create_task(_run_http_async())

    # Run stdio server (blocks until disconnected)
    logger.info("Starting stdio transport...")
    await run_stdio()

    # When stdio ends, cancel HTTP server
    http_task.cancel()
    try:
        await http_task
    except asyncio.CancelledError:
        pass


async def _run_http_async():
    """Run HTTP server as an async task."""
    import uvicorn

    from .http_server import app

    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
    )
    server = uvicorn.Server(config)

    logger.info(f"Starting HTTP transport on {host}:{port}")
    await server.serve()


def main():
    """Main entry point - selects transport based on environment variable."""
    setup_logging()

    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    logger.info(f"Starting MCP server with transport: {transport}")

    if transport == "stdio":
        from .stdio_server import run_stdio

        asyncio.run(run_stdio())

    elif transport == "http":
        from .http_server import run_http

        run_http()

    elif transport == "both":
        asyncio.run(run_both_transports())

    else:
        logger.error(f"Unknown transport: {transport}. Use 'stdio', 'http', or 'both'")
        sys.exit(1)


if __name__ == "__main__":
    main()
