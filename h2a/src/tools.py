from typing import Any, Sequence
from mcp.types import Tool, TextContent
from .prompt_engineering_tool import (
    get_tool as get_prompt_engineering_tool,
    execute as execute_prompt_engineering_tool
)

_tools = {
    "prompt_engineering_assistant": {
        "tool": get_prompt_engineering_tool,
        "execute": execute_prompt_engineering_tool
    }
}


def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return await _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")

