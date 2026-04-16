import sys
import os
from pathlib import Path
from loguru import logger

def setup_logger(log_level: str = "INFO") -> None:

    logger.remove()

    BASE_DIR = Path(__file__).resolve().parent.parent.parent 
    LOG_DIR = BASE_DIR / "logs"

    LOG_DIR.mkdir(exist_ok=True)

    log_file_path = LOG_DIR / "monitor_log.txt"

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        level=log_level,
        format=log_format,
        colorize=True
    )

    logger.add(
        log_file_path,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
        enqueue=True,       
        rotation="10 MB",    
    )

    logger.info(f"Logger configurado com nível: {log_level}")