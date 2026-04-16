# Módulos — Visão Geral

O projeto é organizado em módulos Python com responsabilidades bem definidas:

| Módulo | Caminho | Responsabilidade |
|---|---|---|
| [main.py](main.md) | `app/main.py` | Ponto de entrada; roteamento FastAPI; proxy de páginas |
| [monitor_service.py](monitor_service.md) | `app/services/monitor_service.py` | Loop de polling; detecção de mudança de valor |
| [email_service.py](email_service.md) | `app/services/email_service.py` | Envio de e-mails via SMTP (Gmail) |
| [logger_config.py](logger_config.md) | `app/core/logger_config.py` | Configuração do Loguru (stdout + arquivo) |
| [Interface Web](interface.md) | `app/templates/index.html` | Frontend: iframe proxy + seleção visual de elementos |

---

## Dependências entre Módulos

```
main.py
  ├── importa monitor_service.monitor_price()
  ├── importa logger_config.setup_logger()
  └── serve templates/index.html

monitor_service.py
  └── importa email_service.send_email()

email_service.py
  └── lê variáveis de .env (EMAIL_USER, EMAIL_PASS, ...)

logger_config.py
  └── sem dependências internas
```
