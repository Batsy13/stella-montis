# logger_config.py

**Caminho:** `app/core/logger_config.py`  
**Responsabilidade:** Configura o Loguru para registrar eventos em dois destinos: stdout colorido e arquivo rotativo.

---

## Código Completo

```python
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
| `log_level` | `str` | `"INFO"` | Nível mínimo de log. Aceita `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`, `"CRITICAL"` |

---

## Destinos de Log

### Stdout (Terminal)

```python
logger.add(sys.stdout, level=log_level, format=log_format, colorize=True)
```

Saída colorida no terminal com o seguinte formato:

```
2026-04-15 10:00:00 | INFO     | app.main:index:28 - Application started
2026-04-15 10:05:32 | WARNING  | app.services.monitor_service:monitor_price:45 - Value changed | Old: $74,228.31 | New: $74,231.83
```

Cores por nível:

| Nível | Cor |
|---|---|
| `INFO` | Verde |
| `WARNING` | Amarelo |
| `ERROR` | Vermelho |
| `DEBUG` | Azul |

### Arquivo `logs/monitor_log.txt`

```python
logger.add(
    log_file_path,
    encoding="utf-8",
    enqueue=True,       # thread-safe: enfileira logs assíncronos
    rotation="10 MB",   # cria novo arquivo ao atingir 10 MB
)
```

- **Localização:** `<raiz do projeto>/logs/monitor_log.txt`
- **Encoding:** UTF-8 (suporta caracteres especiais em preços)
- **Rotação:** Arquivo novo criado automaticamente ao atingir 10 MB
- **`enqueue=True`:** Essencial para uso com `asyncio` — o Loguru enfileira as mensagens em uma fila interna e as grava em uma thread separada, evitando bloqueios no event loop

---

## Por que `logger.remove()` é chamado primeiro?

O Loguru adiciona um handler padrão para `stderr` ao ser importado. A chamada `logger.remove()` remove esse handler para que apenas os handlers configurados explicitamente sejam usados.

---

## Exemplo de Arquivo de Log

```
2026-04-09 21:14:01 | INFO     | Application started
2026-04-09 21:14:47 | INFO     | Monitoring requested | URL: https://practice.expandtesting.com/dynamic-table | Selector: #core > ...
2026-04-09 21:14:51 | INFO     | Initial value: 0.7%
2026-04-09 21:15:01 | WARNING  | [2026-04-09 21:15:01] Value changed | Old: 0.7% | New: 8.5%
2026-04-09 21:15:11 | WARNING  | [2026-04-09 21:15:11] Value changed | Old: 8.5% | New: 0.5 MB/s
2026-04-09 21:15:31 | ERROR    | Monitoring error: Locator.is_visible: Target page, context or browser has been closed
```

---

## Evolução entre Branches

=== "feat/logging (versão inicial)"
    ```python
    # Versão simples — sem colorização, rotação em 1 MB, sem nome/função/linha
    logger.add("monitor_log.txt", level="INFO",
               format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
               rotation="1 MB")
    ```

=== "dev (versão final)"
    ```python
    # Versão completa — colorização no stdout, formato detalhado com módulo/função/linha,
    # rotação em 10 MB, enqueue para thread-safety, diretório logs/ criado automaticamente
    logger.add(sys.stdout, colorize=True, format="<green>...</green>...")
    logger.add(log_file_path, enqueue=True, rotation="10 MB", encoding="utf-8")
    ```

As principais melhorias foram:
- Inclusão de `{name}:{function}:{line}` para rastreabilidade precisa
- `enqueue=True` para compatibilidade com `asyncio`
- Rotação aumentada de 1 MB para 10 MB (monitoramentos longos geravam muitos logs)
- Diretório `logs/` criado automaticamente com `LOG_DIR.mkdir(exist_ok=True)`
