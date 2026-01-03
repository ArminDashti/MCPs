import json
import os
import time
from typing import Dict, Any

import httpx

from ..config import Config
from ..utils.logger import log_prompt, log_exception


async def planner(prompt: str) -> str:
    openrouter_planner_key = os.getenv("openrouter_planner_key")
    openrouter_model_name = os.getenv("openrouter_model_name")
    
    headers = {
        "Authorization": f"Bearer {openrouter_planner_key}",
        "Content-Type": "application/json",
    }
    
    instruction = _get_instruction()
    
    full_prompt = f"{instruction}\n\nUser Request:\n{prompt}"
    
    data = {
        "model": openrouter_model_name,
        "messages": [
            {
                "role": "user", 
                "content": full_prompt
            }
        ]    
        }
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
            

def _get_instruction() -> str:
    """Load the instruction for the planner."""
    instruction_path = os.path.join(os.path.dirname(__file__), "..", "instruction.md")
    with open(instruction_path, "r", encoding="utf-8") as f:
        return f.read()


def get_planner_tool():
    """Return the tool definition for the planner."""
    from mcp.types import Tool
    return Tool(
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
    )

# For backward compatibility, also provide a sync version
def planner_sync(prompt: str) -> str:
    """
    Synchronous version of the planner function.
    
    Args:
        prompt: The task or problem that needs planning
        
    Returns:
        A detailed, structured plan with actionable steps
    """
    import asyncio
    
    try:
        # Try to get the current event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in a running loop, we need to run in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, planner(prompt))
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(planner(prompt))
    except Exception as e:
        log_exception(e, f"Error in sync planner: {str(e)}")
        return f"Error: {str(e)}"
