import os
import json
import requests
import asyncio
import time
from typing import Any
from pathlib import Path
from mcp.types import Tool, TextContent
from .config import MODEL, get_log_directory
from .config import TOKEN as API_KEY
from .logger import DailyLogger

API_URL = 'https://openrouter.ai/api/v1/chat/completions'


LOG_DIR = get_log_directory()
logger = DailyLogger(LOG_DIR)

def load_instruction() -> str:
    """Load instruction from the prompt_engineering.md file."""
    instruction_path = Path(__file__).parent / "instruction" / "prompt_engineering.md"
    try:
        with open(instruction_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.log_prompt("", error=f"Instruction file not found: {instruction_path}", model=MODEL)
        raise
    except Exception as e:
        logger.log_prompt("", error=f"Error loading instruction: {str(e)}", model=MODEL)
        raise

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
        logger.log_prompt("", error="human_prompt is required", model=MODEL)
        return [TextContent(
            type="text",
            text=json.dumps({"error": "human_prompt is required"}, indent=2)
        )]

    formatted_prompt = f"The user ask you + {human_prompt} + you MUST rewrite the prompt based on the instruction."

    try:
        instruction = load_instruction()

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

        # Measure response time
        start_time = time.time()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(API_URL, headers=headers, json=payload)
        )
        response_time = time.time() - start_time

        if response.status_code == 200:
            response_data = response.json()
            rewritten_prompt = response_data['choices'][0]['message']['content']
            result = {
                "original_prompt": human_prompt,
                "rewritten_prompt": rewritten_prompt,
                "success": True
            }
            # Log with model and response time
            logger.log_prompt(
                prompt=formatted_prompt,
                response=rewritten_prompt,
                model=MODEL,
                response_time=response_time
            )
        else:
            error_msg = f"API request failed with status code {response.status_code}"
            result = {
                "error": error_msg,
                "details": response.text,
                "success": False
            }
            logger.log_prompt(
                prompt=formatted_prompt,
                error=error_msg,
                model=MODEL,
                response_time=response_time
            )

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
        logger.log_prompt(
            prompt=formatted_prompt if 'formatted_prompt' in locals() else human_prompt,
            error=error_msg,
            model=MODEL
        )
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]

