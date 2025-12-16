import os
import json
import requests
import asyncio
from typing import Any
from mcp.types import Tool, TextContent
from .logger import DailyLogger
from .error_logger import log_error, log_error_message

API_KEY = os.environ.get(
    "OPENROUTER_API_KEY",
    "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"
)
API_URL = 'https://openrouter.ai/api/v1/chat/completions'
MODEL = 'anthropic/claude-haiku-4.5'

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "logs"
)
logger = DailyLogger(LOG_DIR)


def get_tool() -> Tool:
    return Tool(
        name="agent_evaluation_tool",
        description="Evaluates an agent's task performance by comparing user intent, expected actions, and actual actions. The AGENT being evaluated MUST format actions as numbered lines (1. action, 2. action, etc.) and AVOID providing long code - this is strictly enforced.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_intent": {
                    "type": "string",
                    "description": "What the user wanted to accomplish."
                },
                "expected_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of actions the agent should have performed, formatted as numbered steps (1. action, 2. action, etc.)."
                },
                "actual_actions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of actions the agent actually performed, formatted as numbered steps (1. action, 2. action, etc.) showing what was executed."
                }
            },
            "required": ["user_intent", "expected_actions", "actual_actions"]
        }
    )


async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    user_intent = arguments.get("user_intent")
    expected_actions = arguments.get("expected_actions")
    actual_actions = arguments.get("actual_actions")

    if not user_intent or not expected_actions or not actual_actions:
        error_msg = "user_intent, expected_actions, and actual_actions are all required"
        logger.log_evaluation("", "", error=error_msg)
        log_error_message(error_msg, filename="agent_evaluation_tool.py", line_number=56)
        return [TextContent(
            type="text",
            text=json.dumps({"error": error_msg}, indent=2)
        )]

    formatted_prompt = f"""User Intent: {user_intent}

Expected Actions:
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(expected_actions))}

Actual Actions:
{chr(10).join(f"{i+1}. {action}" for i, action in enumerate(actual_actions))}"""

    try:
        instruction = (
            """
            You are an expert evaluator for an agent's task. We called you "Evaluator" and we call the agent which you are evaluating "Agent".
            Your role is to evaluate whether an agent successfully completed its assigned objective by analyzing the provided objective and result.

            AGENT BEHAVIOR REQUIREMENTS (for the agent being evaluated):
            The agent MUST follow these strict rules:
            1. FORMAT: Format expected_actions and actual_actions as numbered lines (1. action, 2. action, etc.)
            2. NO LONG CODE: Agents MUST NOT provide long code blocks or verbose code in their actions/responses
            3. CONCISE RESPONSES: Keep actual_actions brief and focused on what was actually done

            Evaluation Criteria:
            1. CORRECTNESS: Did the agent do what was asked? (correct/partially correct/incorrect)
            2. COMPLETENESS: Did the agent fully address all aspects of the objective?
            3. QUALITY: How well was the task executed? Consider accuracy, clarity, and effectiveness.
            4. EFFICIENCY: Did the agent work efficiently or was there unnecessary complexity?
            5. VALUABLE INFORMATION: Whether the information of the task are valuable to remember or not.

            Response Format:
            Provide your evaluation in the following JSON format:
            {
                "verdict": "correct" | "partially_correct" | "incorrect",
                "correctness_score": 1-10 (10 being perfect),
                "completeness_score": 1-10 (10 being fully complete),
                "quality_score": 1-10 (10 being excellent quality),
                "efficiency_score": 1-10 (10 being highly efficient),
                "overall_score": 1-10 (average of above scores),
                "summary": "Brief summary of the evaluation (2-3 sentences)",
                "strengths": ["List of what was done well"],
                "weaknesses": ["List of areas that need improvement"],
                "advice": "Specific, actionable advice for improving future performance"
                "Final verdict: "Whether the agent is able to continue or must work on the task again and focus on weaknesses."
                "memorizable_information: Whether the information of the task are valuable to remember or not."  
            }

            Be objective and constructive. Focus on what can be learned and improved.
            CRITICAL RULE: STRICTLY penalize the AGENT (not the evaluator) for providing long code blocks or verbose responses.
            Agents must be concise - long code will result in failing evaluation.
            No need for writing long code for the agent. Just provide the feedback in the JSON format.
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
            evaluation_text = response_data['choices'][0]['message']['content']

            # Try to parse as JSON, if it fails, wrap in a JSON structure
            try:
                evaluation_result = json.loads(evaluation_text)
            except json.JSONDecodeError as e:
                log_error(e, filename="agent_evaluation_tool.py", line_number=139)
                evaluation_result = {
                    "evaluation_text": evaluation_text,
                    "parsing_error": "Could not parse evaluation as JSON",
                    "success": True
                }

            final_result = {
                "user_intent": user_intent,
                "expected_actions": expected_actions,
                "actual_actions": actual_actions,
                "evaluation": evaluation_result,
                "success": True
            }
            logger.log_evaluation(user_intent, str(expected_actions) + " | " + str(actual_actions), evaluation_result)
        else:
            error_msg = f"API request failed with status code {response.status_code}"
            log_error_message(error_msg, filename="agent_evaluation_tool.py", line_number=155)
            final_result = {
                "user_intent": user_intent,
                "expected_actions": expected_actions,
                "actual_actions": actual_actions,
                "error": error_msg,
                "details": response.text,
                "success": False
            }
            logger.log_evaluation(user_intent, str(expected_actions) + " | " + str(actual_actions), error=error_msg)

        return [TextContent(
            type="text",
            text=json.dumps(final_result, indent=2, ensure_ascii=False)
        )]

    except Exception as e:
        error_msg = str(e)
        log_error(e, filename="agent_evaluation_tool.py", line_number=171)
        final_result = {
            "user_intent": user_intent,
            "expected_actions": expected_actions,
            "actual_actions": actual_actions,
            "error": error_msg,
            "success": False
        }
        logger.log_evaluation(user_intent, str(expected_actions) + " | " + str(actual_actions), error=error_msg)
        return [TextContent(
            type="text",
            text=json.dumps(final_result, indent=2, ensure_ascii=False)
        )]
