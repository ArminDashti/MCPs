import os
import requests
import json
from typing import Any
from mcp.types import Tool, TextContent

API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'anthropic/claude-haiku-4.5'

def get_tool() -> Tool:
    return Tool(
        name="rewrite_prompt_for_llm",
        description="Rewrites a human prompt to enhance clarity and effectiveness for a Large Language Model (LLM).",
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
        return [TextContent(
            type="text",
            text=json.dumps({"result": "human_prompt is required"}, indent=2)
        )]

    if not API_KEY:
        return [TextContent(
            type="text",
            text=json.dumps({"result": "OPENROUTER_API_KEY environment variable not set."}, indent=2)
        )]

    instruction = (
        """This tool rewrites a human-written prompt into a clearer and 
        more effective version tailored for programming-related tasks. 
        When invoked, the tool transforms the input prompt 
        so that it explicitly states the tool’s focus on software development and 
        instructs the model to provide thorough, precise, and expert-level explanations. 
        The LLM should call this tool only when the user’s request involves improving or 
        reformulating a prompt. """
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": human_prompt}
        ]
    }

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for HTTP errors
        response_data = response.json()
        rewritten_prompt = response_data['choices'][0]['message']['content']
        
        result = {
            "original_prompt": human_prompt,
            "rewritten_prompt": rewritten_prompt
        }
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    except requests.exceptions.RequestException as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"API request failed: {e}", "status_code": getattr(e.response, "status_code", "N/A")}, indent=2)
        )]
    except json.JSONDecodeError as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Failed to decode API response: {e}", "response_text": response.text if response else "N/A"}, indent=2)
        )]
