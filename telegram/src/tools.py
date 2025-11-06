from typing import Any
from mcp.types import Tool, TextContent, Sequence
from fetch_telegram_channel_tool import get_tool as get_fetch_telegram_channel_tool, execute as execute_fetch_telegram_channel

_tools = {
    "fetch_telegram_channel": {
        "tool": get_fetch_telegram_channel_tool,
        "execute": execute_fetch_telegram_channel
    }
}

def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]

async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return await _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")

