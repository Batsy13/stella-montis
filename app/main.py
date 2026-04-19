import asyncio
from pathlib import Path
from typing import Dict
import sys

from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from loguru import logger

from services.monitor_service import monitor_price
from services.selector_service import open_live_selector
from core.logger_config import setup_logger

if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

setup_logger()
class MonitorRequest(BaseModel):
    url: str
    xpath: str

class StopRequest(BaseModel):
    url: str

active_tasks: Dict[str, asyncio.Task] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started and ready for requests")
    
    yield 
    
    logger.info("Application is shutting down. Cleaning up resources...")

app = FastAPI(title="Stella Montis - Price Monitor", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index():
    template_path = TEMPLATES_DIR / "index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Template not found at: {template_path}")
        raise HTTPException(status_code=404, detail="Frontend template missing")

@app.post("/start")
async def start_monitoring(req: MonitorRequest) -> Dict[str, str]:
    logger.info(f"Monitoring requested | URL: {req.url} | Selector: {req.xpath}")
    if req.url in active_tasks:
        active_tasks[req.url].cancel()
    
    task = asyncio.create_task(monitor_price(req.url, req.xpath))
    active_tasks[req.url] = task
    return {"message": "Monitoring started successfully"}

@app.post("/stop")
async def stop_monitoring(req: StopRequest) -> Dict[str, str]:
    logger.info(f"Stop monitoring requested | URL: {req.url}")
    if req.url in active_tasks:
        active_tasks[req.url].cancel()
        del active_tasks[req.url]
        return {"message": "Monitoring stopped successfully"}
    return {"message": "No active monitoring for this URL"}

@app.websocket("/ws/xpath")
async def xpath_websocket(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket: Client conected with the board.")
    
    try:
        while True:
            data = await websocket.receive_json()
            url = data.get("url")
            
            if url:
                logger.info(f"WebSocket: Starting Live Selector to {url}")
                asyncio.create_task(open_live_selector(url, websocket))
                
    except WebSocketDisconnect:
        logger.info("WebSocket: Client disconected.")
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)