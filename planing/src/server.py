import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from .tools import list_tools, call_tool, tool_exists

app = Server("h2a")


@app.list_resources()
async def list_resources() -> list[Resource]:
    return []


@app.read_resource()
async def read_resource(uri: str) -> str:
    raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools_handler() -> Sequence[Tool]:
    return list_tools()


@app.call_tool()
async def call_tool_handler(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # Check if tool exists before calling to ensure proper error handling
    if not tool_exists(name):
        raise ValueError(f"Unknown tool: {name}")
    return await call_tool(name, arguments)


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

