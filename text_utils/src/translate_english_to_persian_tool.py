import json
from typing import Any
from mcp.types import Tool, TextContent
from deep_translator import GoogleTranslator

def get_tool() -> Tool:
    return Tool(
        name="translate_english_to_persian",
        description="Translates text from English to Persian (Farsi).",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The English text to translate to Persian"
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
    
    translator = GoogleTranslator(source='en', target='fa')
    translated_text = translator.translate(text)
    
    result = {
        "original_text": text,
        "translated_text": translated_text,
        "source_language": "english",
        "target_language": "persian"
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2, ensure_ascii=False)
    )]

