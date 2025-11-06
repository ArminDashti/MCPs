import json
from typing import Any
from mcp.types import Tool, TextContent
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def get_tool() -> Tool:
    return Tool(
        name="extract_key_points",
        description="Extracts key points from a given text as a list of important sentences or phrases. Supports English and Persian only.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to extract key points from"
                },
                "max_points": {
                    "type": "integer",
                    "description": "Maximum number of key points to extract (default: 5)",
                    "default": 5
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
    
    max_points = arguments.get("max_points", 5)
    language = arguments.get("language", "english")
    
    if language not in ["english", "persian"]:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Language must be 'english' or 'persian'"}, indent=2)
        )]
    
    if max_points < 1:
        max_points = 1
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        stemmer = Stemmer(language)
        summarizer = TextRankSummarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)
        
        key_point_sentences = summarizer(parser.document, max_points)
        key_points = [str(sentence).strip() for sentence in key_point_sentences]
        
        result = {
            "key_points": key_points,
            "count": len(key_points),
            "language": language,
            "original_length": len(text)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

