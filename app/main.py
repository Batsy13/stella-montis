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

# Internal modules
from services.monitor_service import monitor_price
from services.selector_service import open_live_selector
from core.logger_config import setup_logger

if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

setup_logger()
class MonitorRequest(BaseModel):
    """Schema for starting a price monitoring task.
    
    Attributes:
        url (str): The target website URL.
        xpath (str): The CSS selector or XPath to monitor.
    """
    url: str
    xpath: str

class StopRequest(BaseModel):
    """Schema for stopping a specific monitoring task.
    
    Attributes:
        url (str): The URL identifier for the task to be cancelled.
    """
    url: str

# Dictionary to keep track of background tasks per URL
active_tasks: Dict[str, asyncio.Task] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events.
    
    Yields:
        None: Control back to the FastAPI framework.
    """
    logger.info("Application started and ready for requests")
    
    yield 
    
    logger.info("Application is shutting down. Cleaning up resources...")

app = FastAPI(title="Stella Montis - Price Monitor", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serves the main frontend dashboard.

    Returns:
        str: Raw HTML content from the index.html file.

    Raises:
        HTTPException: If the template file is missing.
    """
    template_path = TEMPLATES_DIR / "index.html"
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Template not found at: {template_path}")
        raise HTTPException(status_code=404, detail="Frontend template missing")

@app.post("/start")
async def start_monitoring(req: MonitorRequest) -> Dict[str, str]:
    """Starts a background task to monitor a price at the given URL.

    Args:
        req (MonitorRequest): Data containing the URL and target selector.

    Returns:
        Dict[str, str]: Confirmation message.
    """
    logger.info(f"Monitoring requested | URL: {req.url} | Selector: {req.xpath}")
    if req.url in active_tasks:
        active_tasks[req.url].cancel()
    
    task = asyncio.create_task(monitor_price(req.url, req.xpath))
    active_tasks[req.url] = task
    return {"message": "Monitoring started successfully"}

@app.post("/stop")
async def stop_monitoring(req: StopRequest) -> Dict[str, str]:
    """Stops an active monitoring task.

    Args:
        req (StopRequest): Data containing the URL of the task to stop.

    Returns:
        Dict[str, str]: Status message of the operation.
    """
    logger.info(f"Stop monitoring requested | URL: {req.url}")
    if req.url in active_tasks:
        active_tasks[req.url].cancel()
        del active_tasks[req.url]
        return {"message": "Monitoring stopped successfully"}
    return {"message": "No active monitoring for this URL"}

@app.websocket("/ws/xpath")
async def xpath_websocket(websocket: WebSocket):
    """Handles the WebSocket connection for the live element selector.

    Allows the user to send a URL to open a browser and pick an element.
    Selected paths are sent back through this same connection.

    Args:
        websocket (WebSocket): The active WebSocket client connection.
    """
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