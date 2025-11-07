from playwright.async_api import async_playwright, Browser, BrowserContext

_browser: Browser | None = None
_context: BrowserContext | None = None

async def init_browser() -> Browser:
    global _browser, _context
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(headless=True)
        _context = await _browser.new_context()
    return _browser

async def close_browser():
    global _browser, _context
    if _browser:
        await _browser.close()
        _browser = None
        _context = None


