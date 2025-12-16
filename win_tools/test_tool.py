import asyncio
import json
from src.html_to_pdf_tool import execute
from src.browser_utils import close_browser

async def main():
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Document</title>
    </head>
    <body>
        <h1>Test PDF Generation</h1>
        <p>This is a test document to verify HTML to PDF conversion.</p>
        <p>It contains multiple paragraphs and formatting.</p>
    </body>
    </html>
    """
    
    print("Testing html_to_pdf tool")
    print("-" * 50)
    
    result = await execute({
        "html_content": test_html,
        "output_path": "test_output.pdf"
    })
    
    if result and len(result) > 0:
        response_text = result[0].text
        print("\nFull JSON Response:")
        print(response_text)
        
        try:
            data = json.loads(response_text)
            if "error" in data:
                print(f"\nError: {data['error']}")
            else:
                print(f"\nSummary:")
                print(f"  Success: {data.get('success', False)}")
                print(f"  Output Path: {data.get('output_path', 'N/A')}")
                print(f"  Message: {data.get('message', 'N/A')}")
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
    else:
        print("No response received")
    
    await close_browser()

if __name__ == "__main__":
    asyncio.run(main())

