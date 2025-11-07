from typing import Any
from mcp.types import Tool, TextContent, Sequence
from extract_main_text_tool import get_tool as get_extract_main_text_tool, execute as execute_extract_main_text

_tools = {
    "extract_main_text": {
        "tool": get_extract_main_text_tool,
        "execute": execute_extract_main_text
    }
}

def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]

async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return await _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")


