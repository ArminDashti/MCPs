import os
import json
import requests
import asyncio
from typing import Any
from mcp.types import Tool, TextContent
from .logger import DailyLogger

API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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"
)
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'kwaipilot/kat-coder-pro:free'

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs"
)
logger = DailyLogger(LOG_DIR)


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
        instruction = (
            """
            - An LLM give you a human-written prompt to rewrite.
            - You must transform and rewrite the human-written prompt into a clearer and
              more effective version tailored for programming-related tasks for an LLM.
            - It explicitly states that the focus is on software development and
            - The rewritten prompt must provide thorough, precise, and expert-level explanations.
            - The user might doesn't write the prompt in a good way, so you must rewrite it in a good way.
            - For example, a user want to create a dropdown in a webapge.
              The human-written prompt: "I want to create a list of items in a box when I click on a it."
              The rewritten prompt: "Create a dropdown list of items."
              You can see the example above to understand how to rewrite the prompt.
              First user doesn't aware of dropdown but second user is aware of it.
            - You must not explain what to do in the prompt. You must rewrite the prompt for an LLM to understand.
              For example, no need to explain how to implement the dropdown in the prompt. You must rewrite the prompt for an LLM to understand.
              Because most of time users don't provide a detailed explanation of the prompt.
            - You must provide some rules for the LLM to follow.
            - You must not provide codes in the prompt.
            - You must always assume the user is a beginner at programming and they don't know how to write a good prompt.
            """
        )

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

