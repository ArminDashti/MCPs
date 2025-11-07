import json
from typing import Any
from mcp.types import Tool, TextContent
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def get_tool() -> Tool:
    return Tool(
        name="summarize_text",
        description="Summarizes a given text using extractive summarization algorithms. Supports English and Persian only.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to summarize"
                },
                "sentence_count": {
                    "type": "integer",
                    "description": "Number of sentences in the summary (default: 3)",
                    "default": 3
                },
                "method": {
                    "type": "string",
                    "description": "Summarization method: 'lsa' (Latent Semantic Analysis) or 'textrank' (TextRank algorithm)",
                    "enum": ["lsa", "textrank"],
                    "default": "lsa"
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
    
    sentence_count = arguments.get("sentence_count", 3)
    method = arguments.get("method", "lsa")
    language = arguments.get("language", "english")
    
    if language not in ["english", "persian"]:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Language must be 'english' or 'persian'"}, indent=2)
        )]
    
    if sentence_count < 1:
        sentence_count = 1
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        stemmer = Stemmer(language)
        
        if method == "lsa":
            summarizer = LsaSummarizer(stemmer)
        else:
            summarizer = TextRankSummarizer(stemmer)
        
        summarizer.stop_words = get_stop_words(language)
        
        summary_sentences = summarizer(parser.document, sentence_count)
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        
        result = {
            "summary": summary,
            "sentence_count": len(summary_sentences),
            "method": method,
            "language": language,
            "original_length": len(text),
            "summary_length": len(summary)
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

