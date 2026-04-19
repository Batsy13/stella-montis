# logger_config.py

**Caminho:** `app/core/logger_config.py`  
**Responsabilidade:** Configura o Loguru para registrar eventos em dois destinos: stdout colorido e arquivo rotativo em `logs/monitor_log.txt`.

---

## Código Completo

```python
import sys
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
```

---

## Função `setup_logger`

### Assinatura

```python
def setup_logger(log_level: str = "INFO") -> None
```

### Parâmetro

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `log_level` | `str` | `"INFO"` | Nível mínimo. Aceita `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |

---

## Destinos de Log

### Stdout (Terminal) — colorido

Formato:
```
2026-04-15 10:00:00 | INFO     | app.main:index:28 - Application started and ready for requests
2026-04-15 10:05:32 | INFO     | app.services.monitor_service:monitor_price:52 - Value changed | Old: $74,228.31 | New: $74,231.83
```

### Arquivo `logs/monitor_log.txt`

- **Localização:** `<raiz do projeto>/logs/monitor_log.txt`
- **Encoding:** UTF-8
- **Rotação:** Novo arquivo ao atingir 10 MB
- **`enqueue=True`:** Thread-safe — essencial para uso com `asyncio`; mensagens são enfileiradas e gravadas em thread separada

---

## Por que `logger.remove()` primeiro?

O Loguru registra um handler padrão para `stderr` ao ser importado. `logger.remove()` limpa todos os handlers antes de adicionar os configurados explicitamente.

---

## Exemplo de Arquivo de Log

```
2026-04-15 10:00:00 | INFO     | Application started and ready for requests
2026-04-15 10:01:15 | INFO     | Starting persistent monitoring | URL: https://coinmarketcap.com/...
2026-04-15 10:01:20 | INFO     | Initial value: $84,512.00
2026-04-15 10:01:30 | INFO     | Value changed | Old: $84,512.00 | New: $84,498.75
2026-04-15 10:05:00 | INFO     | Monitoring task for https://... was cancelled by user/system.
2026-04-15 10:05:00 | INFO     | Resource cleanup finished for https://...
```
