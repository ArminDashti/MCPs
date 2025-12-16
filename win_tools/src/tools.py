from typing import Any
from mcp.types import Tool, TextContent, Sequence
from html_to_pdf_tool import get_tool as get_html_to_pdf_tool, execute as execute_html_to_pdf

_tools = {
    "html_to_pdf": {
        "tool": get_html_to_pdf_tool,
        "execute": execute_html_to_pdf
    }
}

def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]

async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return await _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")

