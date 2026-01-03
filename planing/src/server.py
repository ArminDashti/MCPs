#!/usr/bin/env python3
"""
MCP Planner Server

This module provides the main entry point for the MCP Planner server.
It exposes the planning functionality as an MCP tool.
"""

import asyncio
import sys
from typing import Any, Dict, List
import os

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

from .config import Config
from .tool_registry import list_tools, call_tool, tool_exists


# Create the MCP server
app = Server("mcp-planner")




@app.list_tools()
async def list_tools_handler() -> Sequence[Tool]:
    return list_tools()


@app.call_tool()
async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    if name in loaded_tools:
        try:
            tool_func = get_tool_function(TOOLS_DIR, name)
            # Assuming all tools take a 'prompt' argument for simplicity
            prompt = arguments.get("prompt", "")
            if not prompt:
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=f"Error: 'prompt' argument is required for tool '{name}'.",
                        )
                    ]
                )
            
            result = tool_func(prompt)
            
            return CallToolResult(
                content=[TextContent(type="text", text=result)]
            )
            
        except Exception as e:
            error_msg = f"Error executing tool '{name}': {str(e)}"
            return CallToolResult(
                content=[
                    TextContent(type="text", text=error_msg)
                ]
            )
    
    else:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]
        )


async def main():
    """Main entry point for the MCP server."""
    try:
        # Validate configuration before starting
        print("Validating configuration...", file=sys.stderr)
        Config.validate()
        print("Configuration validated successfully!", file=sys.stderr)

        # Run the server
        print("Starting MCP server...", file=sys.stderr)
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-planner",
                    server_version="0.1.0",
                    capabilities=ServerCapabilities(supports_tools=True),
                )
            )
    except Exception as e:
        import traceback
        print(f"Failed to start MCP Planner server: {e}", file=sys.stderr)
        print(f"Full traceback: {traceback.format_exc()}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
