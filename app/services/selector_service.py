import asyncio
from playwright.async_api import async_playwright
from loguru import logger
from fastapi import WebSocket

async def open_live_selector(url: str, websocket: WebSocket):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0"
        )
        page = await context.new_page()
        
        async def on_xpath_selected(xpath: str):
            logger.success(f"XPath: {xpath}")
            await websocket.send_json({"type": "xpath_result", "xpath": xpath})

        await page.expose_function("sendToPython", on_xpath_selected)
        
        await page.add_init_script("""
            const injectCSS = setInterval(() => {
                if (document.head) {
                    const style = document.createElement('style');
                    style.innerHTML = `
                        .scraper-hover { outline: 2px solid red !important; cursor: crosshair !important; z-index: 2147483647; }
                        .scraper-selected { outline: 3px solid blue !important; background-color: rgba(0,0,255,0.1) !important; z-index: 2147483647; }
                    `;
                    document.head.appendChild(style);
                    clearInterval(injectCSS);
                }
            }, 50);

            document.addEventListener('mouseover', (e) => { e.target.classList.add('scraper-hover'); }, true);
            document.addEventListener('mouseout', (e) => { e.target.classList.remove('scraper-hover'); }, true);

            document.addEventListener('click', (e) => {
                e.preventDefault(); 
                e.stopPropagation();
                
                let el = e.target;
                let path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    let selector = el.nodeName.toLowerCase();
                    if (el.id) {
                        path.unshift('#' + el.id);
                        break;
                    } else {
                        let sib = el, nth = 1;
                        while (sib = sib.previousElementSibling) {
                            if (sib.nodeName.toLowerCase() === selector) nth++;
                        }
                        selector += `:nth-of-type(${nth})`;
                    }
                    path.unshift(selector);
                    el = el.parentNode;
                }
                
                const xpath = path.join(' > ');
                window.sendToPython(xpath); 
            }, true);
        """)
        
        try:
            logger.info("Navigating to the page")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            logger.info("Content Loaded. Waiting user's click")
            
            while browser.is_connected():
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Erro no Live Selector: {e}")
            await websocket.send_json({"type": "error", "message": str(e)})