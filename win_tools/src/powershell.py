import subprocess
import asyncio
import json
from typing import Any, Dict
from mcp.types import Tool


async def execute_powershell_command(command: str, working_directory: str = None) -> dict[str, Any]:
    """Execute a PowerShell command asynchronously.

    Args:
        command: The PowerShell command to execute
        working_directory: Optional working directory for the command

    Returns:
        dict with stdout, stderr, return_code, and execution_time
    """
    import time
    start_time = time.time()

    try:
        # Prepare the PowerShell command
        ps_command = ["powershell", "-Command", command]

        # Set up the process
        process = await asyncio.create_subprocess_exec(
            *ps_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_directory
        )

        # Wait for completion and get output
        stdout, stderr = await process.communicate()

        execution_time = time.time() - start_time

        # Decode output
        stdout_text = stdout.decode('utf-8', errors='replace').strip()
        stderr_text = stderr.decode('utf-8', errors='replace').strip()

        return {
            "stdout": stdout_text,
            "stderr": stderr_text,
            "return_code": process.returncode,
            "execution_time": execution_time,
            "success": process.returncode == 0
        }

    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1,
            "execution_time": execution_time,
            "success": False
        }


def get_tool() -> Tool:
    return Tool(
        name="execute_powershell",
        description="Execute PowerShell commands on Windows. Supports running any PowerShell command or script with optional working directory.",
        inputSchema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The PowerShell command to execute"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Optional working directory where the command should be executed"
                }
            },
            "required": ["command"]
        }
    )