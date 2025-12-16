from typing import Any, Sequence
from mcp.types import Tool, TextContent
from .agent_evaluation_tool import (
    get_tool as get_agent_evaluation_tool,
    execute as execute_agent_evaluation_tool
)
from .error_logger import log_error

_tools = {
    "agent_evaluation_tool": {
        "tool": get_agent_evaluation_tool,
        "execute": execute_agent_evaluation_tool
    }
}


def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    try:
        if name in _tools:
            return await _tools[name]["execute"](arguments)
        error = ValueError(f"Unknown tool: {name}")
        log_error(error, filename="tools.py", line_number=23)
        raise error
    except Exception as e:
        log_error(e, filename="tools.py", line_number=20)
        raise
