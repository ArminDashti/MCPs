from typing import Any, Sequence
from mcp.types import Tool, TextContent
from .tools.planner import planner_sync

_tools = {
    "planner": {
        "tool": lambda: Tool(
            name="planner",
            description="Generate comprehensive plans for tasks, projects, or problems using AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The task, project, or problem that needs planning",
                    },
                },
                "required": ["prompt"],
            },
        ),
        "execute": lambda arguments: [TextContent(type="text", text=planner_sync(arguments.get("prompt", "")))],
    }
}


def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]


def tool_exists(name: str) -> bool:
    """Check if a tool with the given name exists."""
    return name in _tools


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")