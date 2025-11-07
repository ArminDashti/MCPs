import asyncio
import json
import os
import shutil
import sys
from asyncio import subprocess as aio_subprocess
from typing import Any
import time
from mcp.types import Tool, TextContent

def get_tool() -> Tool:
    return Tool(
        name="run_python_code",
        description="Executes Python code inside the py312 conda environment",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python source code to execute"
                }
            },
            "required": ["code"]
        }
    )

async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    code = arguments.get("code")
    if not code:
        return [TextContent(
            type="text",
            text=json.dumps({"time": 0.0, "result": "code is required"}, indent=2)
        )]
    command = ["conda", "run", "-n", "py312", "python", "-c", code]
    if not shutil.which(command[0]):
        if shutil.which("py"):
            command = ["py", "-3.12", "-c", code]
        else:
            command = [sys.executable, "-c", code]
    elif os.name == "nt":
        command = ["cmd.exe", "/C", *command]
    start = time.perf_counter()
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=aio_subprocess.PIPE,
        stderr=aio_subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    elapsed = time.perf_counter() - start
    stdout_text = stdout.decode().replace("\r", "")
    stderr_text = stderr.decode().replace("\r", "")
    stdout_lines = [line for line in stdout_text.split("\n") if line]
    result_text = stdout_lines[-1] if stdout_lines else stderr_text.strip()
    result = {
        "time": elapsed,
        "is_successful": 1 if process.returncode == 0 else 0,
        "result": result_text
    }
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]

