from typing import Any, Sequence
from mcp.types import Tool, TextContent
from .powershell import (
    get_tool as get_powershell_tool,
    execute_powershell_command as execute_powershell_tool
)

_tools = {
    "powershell": {
        "tool": get_powershell_tool,
        "execute": execute_powershell_tool
    }
}


def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]


def tool_exists(name: str) -> bool:
    """Check if a tool with the given name exists."""
    return name in _tools


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        result = await _tools[name]["execute"](**arguments)
        
        # Format the result as a JSON string for better readability
        result_json = {
            "command": arguments.get("command", ""),
            "working_directory": arguments.get("working_directory", ""),
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "return_code": result["return_code"],
            "execution_time": round(result["execution_time"], 3),
            "success": result["success"]
        }
        
        formatted_output = f"""PowerShell Command Execution Results:
========================================
Command: {result_json['command']}
Working Directory: {result_json['working_directory'] or 'Default'}
Return Code: {result_json['return_code']}
Execution Time: {result_json['execution_time']}s
Success: {result_json['success']}

STDOUT:
{result_json['stdout'] or '(empty)'}

STDERR:
{result_json['stderr'] or '(empty)'}
========================================"""
        
        return [TextContent(type="text", text=formatted_output)]
    
    raise ValueError(f"Unknown tool: {name}")
