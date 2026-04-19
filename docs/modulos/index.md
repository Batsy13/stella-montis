# Módulos — Visão Geral

O projeto é organizado em módulos Python com responsabilidades bem definidas:

| Módulo | Caminho | Responsabilidade |
|---|---|---|
| [main.py](main.md) | `app/main.py` | Ponto de entrada; roteamento REST + WebSocket; gerenciamento de tasks |
| [monitor_service.py](monitor_service.md) | `app/services/monitor_service.py` | Loop de polling; detecção de mudança; notificação via Google Forms |
| [selector_service.py](selector_service.md) | `app/services/selector_service.py` | Live Selector: abre browser real, captura CSS selector via WebSocket |
| [logger_config.py](logger_config.md) | `app/core/logger_config.py` | Configuração do Loguru (stdout + arquivo) |
| [Interface Web](interface.md) | `app/templates/index.html` | Frontend: WebSocket client, start/stop, exibição do selector |

---

## Dependências entre Módulos

```
main.py
  ├── importa monitor_service.monitor_price()
  ├── importa selector_service.open_live_selector()
  ├── importa logger_config.setup_logger()
  └── serve templates/index.html

monitor_service.py
  └── sem dependências internas
      (notifica via requests.post + Playwright direto)

selector_service.py
  └── recebe WebSocket de main.py

logger_config.py
  └── sem dependências internas
```
