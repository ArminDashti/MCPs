import asyncio
import json
from src.extract_main_text_tool import execute
from src.browser_utils import close_browser

async def main():
    test_url = "https://www.bbc.com/persian/articles/c0r0j81d542o"
    output_lines = []
    
    output_lines.append(f"Extracting main text from: {test_url}")
    output_lines.append("-" * 50)
    print(f"Extracting main text from: {test_url}")
    print("-" * 50)
    
    result = await execute({"url": test_url})
    
    if result and len(result) > 0:
        response_text = result[0].text
        output_lines.append("\nFull JSON Response:")
        output_lines.append(response_text)
        print("\nFull JSON Response:")
        print(response_text)
        
        try:
            data = json.loads(response_text)
            if "error" in data:
                error_msg = f"\nError: {data['error']}"
                output_lines.append(error_msg)
                print(error_msg)
            else:
                output_lines.append("\nSummary:")
                output_lines.append(f"  URL: {data.get('url', 'N/A')}")
                output_lines.append(f"  Title: {data.get('title', 'N/A')}")
                output_lines.append(f"  Author: {data.get('author', 'N/A')}")
                output_lines.append(f"  Date: {data.get('date', 'N/A')}")
                output_lines.append(f"  Text Length: {data.get('length', 0)} characters")
                print("\nSummary:")
                print(f"  URL: {data.get('url', 'N/A')}")
                print(f"  Title: {data.get('title', 'N/A')}")
                print(f"  Author: {data.get('author', 'N/A')}")
                print(f"  Date: {data.get('date', 'N/A')}")
                print(f"  Text Length: {data.get('length', 0)} characters")
                if data.get('text'):
                    preview = data['text'][:200] + "..." if len(data['text']) > 200 else data['text']
                    preview_msg = f"\nText Preview:\n  {preview}"
                    output_lines.append(preview_msg)
                    print(f"\nText Preview:")
                    print(f"  {preview}")
        except json.JSONDecodeError:
            error_msg = "Failed to parse JSON response"
            output_lines.append(error_msg)
            print(error_msg)
    else:
        error_msg = "No response received"
        output_lines.append(error_msg)
        print(error_msg)
    
    with open("C:/Users/Armin/Desktop/test_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print(f"\nOutput saved to C:/Users/Armin/Desktop/test_output.txt")
    
    await close_browser()

if __name__ == "__main__":
    asyncio.run(main())

