import json
from typing import Any
from mcp.types import Tool, TextContent
from deep_translator import GoogleTranslator

def get_tool() -> Tool:
    return Tool(
        name="translate_persian_to_english",
        description="Translates text from Persian (Farsi) to English.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The Persian text to translate to English"
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
    
    translator = GoogleTranslator(source='fa', target='en')
    translated_text = translator.translate(text)
    
    result = {
        "original_text": text,
        "translated_text": translated_text,
        "source_language": "persian",
        "target_language": "english"
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2, ensure_ascii=False)
    )]

