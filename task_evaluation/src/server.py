import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from .tools import list_tools, call_tool
from .error_logger import log_error

app = Server("agent_evaluator")


@app.list_resources()
async def list_resources() -> list[Resource]:
    return []


@app.read_resource()
async def read_resource(uri: str) -> str:
    error = ValueError(f"Unknown resource: {uri}")
    log_error(error, filename="server.py", line_number=18)
    raise error


@app.list_tools()
async def list_tools_handler() -> Sequence[Tool]:
    return list_tools()


@app.call_tool()
async def call_tool_handler(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        return await call_tool(name, arguments)
    except Exception as e:
        log_error(e, filename="server.py", line_number=28)
        raise


async def main():
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        log_error(e, filename="server.py", line_number=32)
        raise


if __name__ == "__main__":
    asyncio.run(main())
