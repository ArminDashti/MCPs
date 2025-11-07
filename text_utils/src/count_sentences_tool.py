import json
from typing import Any
from mcp.types import Tool, TextContent
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

def get_tool() -> Tool:
    return Tool(
        name="count_sentences",
        description="Counts the number of sentences in a given text. Supports English and Persian only.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count sentences in"
                },
                "language": {
                    "type": "string",
                    "description": "Language code: 'english' or 'persian'. Default: 'english'",
                    "enum": ["english", "persian"],
                    "default": "english"
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
    
    language = arguments.get("language", "english")
    if language not in ["english", "persian"]:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Language must be 'english' or 'persian'"}, indent=2)
        )]
    
    parser = PlaintextParser.from_string(text, Tokenizer(language))
    sentence_count = len(parser.document.sentences)
    
    result = {
        "sentence_count": sentence_count,
        "language": language,
        "text_length": len(text)
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2, ensure_ascii=False)
    )]

