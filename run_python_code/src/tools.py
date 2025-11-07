from typing import Any, Sequence
from mcp.types import Tool, TextContent
from .run_python_code_tool import get_tool as get_run_python_code_tool, execute as execute_run_python_code

_tools = {
    "run_python_code": {
        "tool": get_run_python_code_tool,
        "execute": execute_run_python_code
    }
}

def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]

async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return await _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")

