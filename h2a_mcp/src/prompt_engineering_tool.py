import os
import json
import requests
import asyncio
from typing import Any
from pathlib import Path
from mcp.types import Tool, TextContent
from .logger import DailyLogger
from .config import API_KEY, MODEL, LOG_DIR

INSTRUCTION_DIR = Path(__file__).parent / "instruction"


def load_instruction(filename: str) -> str:
    """Load instruction from a file in the instruction directory."""
    instruction_path = INSTRUCTION_DIR / filename
    if not instruction_path.exists():
        raise FileNotFoundError(f"Instruction file not found: {instruction_path}")
    with open(instruction_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_tool() -> Tool:
    return Tool(
        name="prompt_engineering_assistant",
        description="Rewrites a human prompt for an LLM to enhance clarity and effectiveness.",
        inputSchema={
            "type": "object",
            "properties": {
                "human_prompt": {
                    "type": "string",
                    "description": "The human-written prompt to be rewritten."
                }
            },
            "required": ["human_prompt"]
        }
    )


async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    human_prompt = arguments.get("human_prompt")
    if not human_prompt:
        logger.log_prompt("", error="human_prompt is required")
        return [TextContent(
            type="text",
            text=json.dumps({"error": "human_prompt is required"}, indent=2)
        )]

    formatted_prompt = f"The user ask me + {human_prompt} + please explain the user prompt."

    try:
        instruction = load_instruction("prompt_engineering.txt")

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": instruction},
                {"role": "user", "content": formatted_prompt}
            ]
        }

        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(API_URL, headers=headers, json=payload)
        )

        if response.status_code == 200:
            response_data = response.json()
            rewritten_prompt = response_data['choices'][0]['message']['content']
            result = {
                "original_prompt": human_prompt,
                "rewritten_prompt": rewritten_prompt,
                "success": True
            }
            logger.log_prompt(human_prompt, rewritten_prompt)
        else:
            error_msg = f"API request failed with status code {response.status_code}"
            result = {
                "error": error_msg,
                "details": response.text,
                "success": False
            }
            logger.log_prompt(human_prompt, error=error_msg)

        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

    except Exception as e:
        error_msg = str(e)
        result = {
            "error": error_msg,
            "success": False
        }
        logger.log_prompt(human_prompt, error=error_msg)
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

