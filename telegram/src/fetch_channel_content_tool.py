import json
import re
from typing import Any
from mcp.types import Tool, TextContent
from .browser_utils import init_browser

def get_tool() -> Tool:
    return Tool(
        name="fetch_telegram_channel",
        description="Opens a Telegram channel page and fetches the data into JSON format",
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The Telegram channel URL (e.g., https://t.me/channelname or https://web.telegram.org/k/#@channelname)"
                }
            },
            "required": ["url"]
        }
    )

def extract_channel_data(page_content: str, url: str) -> dict:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page_content, 'lxml')
    
    data = {
        "channel_name": None,
        "channel_username": None,
        "posts": []
    }
    
    title_elem = soup.find('div', class_='tgme_channel_info_header_title') or soup.find('h1', class_='tgme_channel_info_header_title')
    if title_elem:
        data["channel_name"] = title_elem.get_text(strip=True)
    
    username_elem = soup.find('div', class_='tgme_channel_info_header_username')
    if username_elem:
        username_text = username_elem.get_text(strip=True)
        if username_text.startswith('@'):
            data["channel_username"] = username_text
    
    post_elements = soup.find_all('div', class_='tgme_widget_message')
    
    for post in post_elements:
        post_data = {
            "datetime": None,
            "textcontent": None,
            "imgs": [],
            "video": False,
            "views": None,
            "link": None
        }
        
        date_elem = post.find('time', class_='tgme_widget_message_date')
        if date_elem:
            post_data["datetime"] = date_elem.get('datetime') or date_elem.get_text(strip=True)
        
        text_elem = post.find('div', class_='tgme_widget_message_text')
        if text_elem:
            post_data["textcontent"] = text_elem.get_text(strip=True)
        
        img_urls = []
        
        img_elems = post.find_all('img')
        for img in img_elems:
            src = img.get('src')
            if src and ('telegram-cdn.org' in src or 'telegram.org' in src or 'cdn4.telegram-cdn.org' in src):
                if src not in img_urls:
                    img_urls.append(src)
        
        photo_wrap = post.find('a', class_='tgme_widget_message_photo_wrap')
        if photo_wrap:
            style = photo_wrap.get('style', '')
            bg_match = re.search(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
            if bg_match:
                bg_url = bg_match.group(1)
                if bg_url not in img_urls:
                    img_urls.append(bg_url)
        
        if img_urls:
            post_data["imgs"] = img_urls
        
        video_elem = post.find('video') or post.find('div', class_='tgme_widget_message_video_wrap') or post.find('a', class_='tgme_widget_message_video_wrap')
        if video_elem:
            post_data["video"] = True
        
        views_elem = post.find('span', class_='tgme_widget_message_views')
        if views_elem:
            views_text = views_elem.get_text(strip=True)
            post_data["views"] = views_text
        
        link_elem = post.find('a', class_='tgme_widget_message_date')
        if link_elem:
            href = link_elem.get('href')
            if href:
                post_data["link"] = href
        
        if not post_data["imgs"]:
            del post_data["imgs"]
        
        data["posts"].append(post_data)
    
    return data

async def execute(arguments: dict[str, Any]) -> list[TextContent]:
    url = arguments.get("url")
    if not url:
        return [TextContent(
            type="text",
            text=json.dumps({"error": "URL is required"}, indent=2)
        )]
    
    if not url.startswith("http"):
        if url.startswith("@"):
            url = f"https://t.me/{url[1:]}"
        elif url.startswith("t.me/"):
            url = f"https://{url}"
        else:
            url = f"https://t.me/{url}"
    
    browser = await init_browser()
    page = await browser.new_page()
    
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector('div.tgme_widget_message', timeout=30000)
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        channel_data = extract_channel_data(content, url)
        
        return [TextContent(
            type="text",
            text=json.dumps(channel_data, indent=2, ensure_ascii=False)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]
    finally:
        await page.close()

