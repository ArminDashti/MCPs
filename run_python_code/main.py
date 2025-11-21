"""Dedicated MCP server entry point - avoids circular imports and double-loading."""
import asyncio
from src.server import main as start_server

if __name__ == "__main__":
    asyncio.run(start_server())

