import json
import os
from pathlib import Path
from typing import Any
from mcp.types import Tool, TextContent
from .browser_utils import init_browser

def get_tool() -> Tool:
    return Tool(
        name="html_to_pdf",
        description="Converts HTML content or HTML file to PDF format",
        inputSchema={
            "type": "object",
            "properties": {
                "html_content": {
                    "type": "string",
                    "description": "HTML content as string to convert to PDF"
                },
                "html_file": {
                    "type": "string",
                    "description": "Path to HTML file to convert to PDF"
                },
                "output_path": {
                    "type": "string",
                    "description": "Output path for the PDF file (default: output.pdf in current directory)"
                }
            },
            "required": []
        }
    )

async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    html_content = arguments.get("html_content")
    html_file = arguments.get("html_file")
    output_path = arguments.get("output_path", "output.pdf")
    
    if not html_content and not html_file:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "Either html_content or html_file must be provided"}, indent=2)
        )]
    
    if html_file and not os.path.exists(html_file):
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"HTML file not found: {html_file}"}, indent=2)
        )]
    
    browser = await init_browser()
    page = await browser.new_page()
    
    try:
        if html_file:
            file_path = Path(html_file).resolve()
            await page.goto(f"file:///{file_path.as_posix()}", wait_until="networkidle")
        else:
            await page.set_content(html_content, wait_until="networkidle")
        
        output_file = Path(output_path).resolve()
        await page.pdf(path=str(output_file))
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "output_path": str(output_file),
                "message": f"PDF created successfully at {output_file}"
            }, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]
    finally:
        await page.close()

