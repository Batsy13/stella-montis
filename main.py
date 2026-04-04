from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from playwright.async_api import async_playwright
import uvicorn
import re
from monitor import monitor_price

app = FastAPI()

class MonitorRequest(BaseModel):
    url: str
    xpath: str

@app.post("/start")
async def start_monitoring(req: MonitorRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(monitor_price, req.url, req.xpath)
    return {"message": "Monitoring started"}

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r") as f:
        return f.read()

@app.get("/proxy", response_class=HTMLResponse)
async def proxy(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="load", timeout=15000)
            await page.wait_for_timeout(5000)
        except:
            pass
        html = await page.content()
        await browser.close()
        
    html = re.sub(r'<meta[^>]*http-equiv=["\']?(Content-Security-Policy|X-Frame-Options)["\']?[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html, flags=re.IGNORECASE)
        
    base_tag = f'<base href="{url}">'
    
    script = """
    <style>
        .scraper-hover { outline: 2px solid red !important; cursor: crosshair !important; }
        .scraper-selected { outline: 3px solid blue !important; background-color: rgba(0, 0, 255, 0.1) !important; }
    </style>
    <script>
    let selectedElement = null;

    document.addEventListener('mouseover', function(e) {
        e.target.classList.add('scraper-hover');
    }, true);

    document.addEventListener('mouseout', function(e) {
        e.target.classList.remove('scraper-hover');
    }, true);

    document.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (selectedElement) {
            selectedElement.classList.remove('scraper-selected');
        }
        selectedElement = e.target;
        selectedElement.classList.add('scraper-selected');
        
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
        
        let finalSelector = path.join(' > ');
        window.parent.postMessage({xpath: finalSelector}, '*');
    }, true);
    </script>
    """
    
    if "<head>" in html:
        html = html.replace("<head>", f"<head>{base_tag}")
    else:
        html = base_tag + html
        
    if "</body>" in html:
        html = html.replace("</body>", f"{script}</body>")
    else:
        html += script
        
    return html

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)