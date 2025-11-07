import json
from typing import Any
from mcp.types import Tool, TextContent

def get_tool() -> Tool:
    return Tool(
        name="count_paragraphs",
        description="Counts the number of paragraphs in a given text",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count paragraphs in"
                }
            },
            "required": ["text"]
        }
    )

async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    text = arguments.get("text")
    if not text:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Text is required"}, indent=2)
        )]
    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    paragraph_count = len(paragraphs) if paragraphs else 1 if text.strip() else 0
    
    result = {
        "paragraph_count": paragraph_count,
        "text_length": len(text)
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2, ensure_ascii=False)
    )]

