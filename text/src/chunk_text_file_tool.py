import json
import os
from typing import Any
from mcp.types import Tool, TextContent

def get_tool() -> Tool:
    return Tool(
        name="chunk_text_file",
        description="Splits a text file into chunks of specified size. Returns an array of text chunks.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the text file to chunk"
                },
                "chunk_size": {
                    "type": "integer",
                    "description": "Size of each chunk in characters (default: 1000)",
                    "default": 1000
                },
                "overlap": {
                    "type": "integer",
                    "description": "Number of characters to overlap between chunks (default: 0)",
                    "default": 0
                }
            },
            "required": ["file_path"]
        }
    )

async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    file_path = arguments.get("file_path")
    if not file_path:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "File path is required"}, indent=2)
        )]
    
    if not os.path.exists(file_path):
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"File not found: {file_path}"}, indent=2)
        )]
    
    chunk_size = arguments.get("chunk_size", 1000)
    overlap = arguments.get("overlap", 0)
    
    if chunk_size < 1:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Chunk size must be at least 1"}, indent=2)
        )]
    
    if overlap < 0:
        overlap = 0
    
    if overlap >= chunk_size:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Overlap must be less than chunk size"}, indent=2)
        )]
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunks = []
    start = 0
    content_length = len(content)
    
    while start < content_length:
        end = min(start + chunk_size, content_length)
        chunk = content[start:end]
        chunks.append(chunk)
        
        if end >= content_length:
            break
        
        start = end - overlap
    
    result = {
        "file_path": file_path,
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "total_characters": content_length,
        "chunks": chunks
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, indent=2, ensure_ascii=False)
    )]

