import asyncio
import json
from src.fetch_telegram_channel_tool import execute
from src.browser_utils import close_browser

async def main():
    test_url = "https://t.me/s/Akharin_khodro"
    
    print(f"Fetching Telegram channel: {test_url}")
    print("-" * 50)
    
    result = await execute({"url": test_url})
    
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
                print(f"  Channel Name: {data.get('channel_name', 'N/A')}")
                print(f"  Channel Username: {data.get('channel_username', 'N/A')}")
                print(f"  Number of posts: {len(data.get('posts', []))}")
                if data.get('posts'):
                    print(f"\nFirst post:")
                    first_post = data['posts'][0]
                    print(f"  - Datetime: {first_post.get('datetime', 'N/A')}")
                    print(f"  - Text: {first_post.get('textcontent', 'N/A')}")
                    print(f"  - Views: {first_post.get('views', 'N/A')}")
                    if first_post.get('imgs'):
                        print(f"  - Images: {len(first_post['imgs'])}")
                    if first_post.get('video'):
                        print(f"  - Has video: Yes")
        except json.JSONDecodeError:
            print("Failed to parse JSON response")
    else:
        print("No response received")
    
    await close_browser()

if __name__ == "__main__":
    asyncio.run(main())

