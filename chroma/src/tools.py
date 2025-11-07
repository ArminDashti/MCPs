from __future__ import annotations

from typing import Any, Sequence

from mcp.types import TextContent, Tool

from .add_tool import execute as execute_add, get_tool as get_add_tool
from .query_tool import execute as execute_query, get_tool as get_query_tool


_TOOLS: dict[str, dict[str, Any]] = {
    "chroma_add": {
        "tool": get_add_tool,
        "execute": execute_add
    },
    "chroma_query": {
        "tool": get_query_tool,
        "execute": execute_query
    }
}


def list_tools() -> Sequence[Tool]:
    return [descriptor["tool"]() for descriptor in _TOOLS.values()]


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name not in _TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    return await _TOOLS[name]["execute"](arguments)

