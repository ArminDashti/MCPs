import json
from typing import Any
from mcp.types import Tool, TextContent
from .browser_utils import init_browser
import trafilatura

def get_tool() -> Tool:
    return Tool(
        name="extract_main_text",
        description="Extracts the main text content from a web page URL, removing navigation, ads, and other non-content elements",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the web page to extract text from"
                },
                "include_comments": {
                    "type": "boolean",
                    "description": "Whether to include comments in the extracted text (default: false)",
                    "default": False
                },
                "include_tables": {
                    "type": "boolean",
                    "description": "Whether to include tables in the extracted text (default: true)",
                    "default": True
                },
                "include_images": {
                    "type": "boolean",
                    "description": "Whether to include image alt text in the extracted text (default: false)",
                    "default": False
                }
            },
            "required": ["url"]
        }
    )

async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    url = arguments.get("url")
    if not url:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "URL is required"}, indent=2)
        )]
    
    include_comments = arguments.get("include_comments", False)
    include_tables = arguments.get("include_tables", True)
    include_images = arguments.get("include_images", False)
    
    browser = await init_browser()
    page = await browser.new_page()
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        
        html_content = await page.content()
        
        extracted = trafilatura.extract(
            html_content,
            include_comments=include_comments,
            include_tables=include_tables,
            include_images=include_images,
            output_format="text"
        )
        
        if not extracted:
            metadata = trafilatura.extract_metadata(html_content)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Could not extract main text content from the page",
                    "url": url,
                    "title": metadata.title if metadata else None
                }, indent=2)
            )]
        
        metadata = trafilatura.extract_metadata(html_content)
        
        result = {
            "url": url,
            "text": extracted,
            "title": metadata.title if metadata else None,
            "author": metadata.author if metadata else None,
            "date": metadata.date if metadata else None,
            "length": len(extracted)
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e), "url": url}, indent=2)
        )]
    finally:
        await page.close()

