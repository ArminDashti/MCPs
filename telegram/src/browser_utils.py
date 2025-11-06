from playwright.async_api import Browser

browser_instance: Browser | None = None
playwright_instance = None

async def init_browser():
    global browser_instance, playwright_instance
    if browser_instance is None:
        from playwright.async_api import async_playwright
        playwright_instance = await async_playwright().start()
        browser_instance = await playwright_instance.chromium.launch(headless=True)
    return browser_instance

async def close_browser():
    global browser_instance, playwright_instance
    if browser_instance:
        await browser_instance.close()
        browser_instance = None
    if playwright_instance:
        await playwright_instance.stop()
        playwright_instance = None

