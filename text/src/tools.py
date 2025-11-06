from typing import Any
from mcp.types import Tool, TextContent, Sequence
from summarize_text_tool import get_tool as get_summarize_text_tool, execute as execute_summarize_text
from extract_key_points_tool import get_tool as get_extract_key_points_tool, execute as execute_extract_key_points
from count_tokens_tool import get_tool as get_count_tokens_tool, execute as execute_count_tokens
from count_paragraphs_tool import get_tool as get_count_paragraphs_tool, execute as execute_count_paragraphs
from count_sentences_tool import get_tool as get_count_sentences_tool, execute as execute_count_sentences
from translate_persian_to_english_tool import get_tool as get_translate_persian_to_english_tool, execute as execute_translate_persian_to_english
from translate_english_to_persian_tool import get_tool as get_translate_english_to_persian_tool, execute as execute_translate_english_to_persian
from chunk_text_file_tool import get_tool as get_chunk_text_file_tool, execute as execute_chunk_text_file

_tools = {
    "summarize_text": {
        "tool": get_summarize_text_tool,
        "execute": execute_summarize_text
    },
    "extract_key_points": {
        "tool": get_extract_key_points_tool,
        "execute": execute_extract_key_points
    },
    "count_tokens": {
        "tool": get_count_tokens_tool,
        "execute": execute_count_tokens
    },
    "count_paragraphs": {
        "tool": get_count_paragraphs_tool,
        "execute": execute_count_paragraphs
    },
    "count_sentences": {
        "tool": get_count_sentences_tool,
        "execute": execute_count_sentences
    },
    "translate_persian_to_english": {
        "tool": get_translate_persian_to_english_tool,
        "execute": execute_translate_persian_to_english
    },
    "translate_english_to_persian": {
        "tool": get_translate_english_to_persian_tool,
        "execute": execute_translate_english_to_persian
    },
    "chunk_text_file": {
        "tool": get_chunk_text_file_tool,
        "execute": execute_chunk_text_file
    }
}

def list_tools() -> Sequence[Tool]:
    return [tool_info["tool"]() for tool_info in _tools.values()]

async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name in _tools:
        return await _tools[name]["execute"](arguments)
    raise ValueError(f"Unknown tool: {name}")

