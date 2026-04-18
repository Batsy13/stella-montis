import asyncio
from datetime import datetime
from playwright.async_api import async_playwright, Error as PlaywrightError
from loguru import logger
from services.email_service import send_email

async def monitor_price(url: str, selector: str, email: str, interval: int = 10):
    logger.info(f"Starting persistent monitoring | URL: {url}")

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_subject = "Monitoramento Iniciado"
    start_message = f"O monitoramento para a URL {url} foi iniciado com sucesso às {start_time}."
    
    asyncio.create_task(asyncio.to_thread(send_email, email, start_subject, start_message))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context()
        page = await context.new_page()
        
        last_value = None
        
        try:
            await page.goto(url, wait_until="load", timeout=30000)
            
            while True:
                try:
                    locator = page.locator(selector).first
                    
                    if await locator.is_visible():
                        current_value = (await locator.inner_text()).strip()
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        if current_value:
                            if last_value is None:
                                last_value = current_value
                                logger.info(f"Initial value: {current_value}")
                            
                            elif current_value != last_value:
                                log_msg = f"[{now}] Value changed | Old: {last_value} | New: {current_value}"
                                logger.info(log_msg)

                                subject = "Valor alterado!"
                                message = (
                                    f"O valor monitorado foi alterado.\n\n"
                                    f"URL: {url}\n"
                                    f"Data: {now}\n\n"
                                    f"Valor antigo: {last_value}\n"
                                    f"Novo valor: {current_value}"
                                )

                                asyncio.create_task(
                                    asyncio.to_thread(send_email, email, subject, message)
                                )
                                last_value = current_value
                    
                    await asyncio.sleep(interval)
                    
                except PlaywrightError as e:
                    if "closed" in str(e).lower():
                        logger.info("Playwright connection closed. Finishing task.")
                        break
                    raise e 
                    
        except asyncio.CancelledError:
            logger.info(f"Monitoring task for {url} was cancelled by user/system.")
        except Exception as e:
            logger.error(f"Unexpected monitoring error: {e}")
        finally:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            end_subject = "Monitoramento Finalizado"
            end_message = f"O monitoramento para a URL {url} foi encerrado às {end_time}."
            
            try:
                await asyncio.to_thread(send_email, email, end_subject, end_message)
            except Exception as e:
                logger.error(f"Could not send termination email: {e}")

            try:
                if not browser.is_connected():
                    logger.info("Browser already disconnected.")
                else:
                    await browser.close()
            except:
                pass 
            logger.info(f"Resource cleanup finished for {url}")