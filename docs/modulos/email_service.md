# email_service.py

**Caminho:** `app/services/email_service.py`  
**Responsabilidade:** Envio de e-mails transacionais via SMTP (Gmail). Notifica o usuário sobre início, mudanças de valor e encerramento do monitoramento.

---

## Código Completo

```python
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class EmailConfig:
    USER: Optional[str] = os.getenv("EMAIL_USER")
    PASS: Optional[str] = os.getenv("EMAIL_PASS")
    SMTP_SERVER: str = os.getenv("EMAIL_SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT"))

def send_email(to_email: str, subject: str, message_body: str, is_html: bool = False) -> bool:
    if not EmailConfig.USER or not EmailConfig.PASS:
        logger.error("Email credentials missing in environment variables.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EmailConfig.USER
    msg["To"] = to_email

    part = MIMEText(message_body, "html" if is_html else "plain")
    msg.attach(part)

    try:
        with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT, timeout=15) as server:
            server.set_debuglevel(0)
            server.starttls()
            server.login(EmailConfig.USER, EmailConfig.PASS)
            server.send_message(msg)
        return True

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP Authentication failed: Check EMAIL_USER and EMAIL_PASS (App Password).")
    except smtplib.SMTPConnectError:
        logger.error(f"Could not connect to SMTP server {EmailConfig.SMTP_SERVER}.")
    except Exception as e:
        logger.error(f"Unexpected error in email service: {e}")

    return False
```

---

## Classe `EmailConfig`

Centraliza a leitura das variáveis de ambiente de configuração SMTP. Carregada uma vez no import do módulo via `load_dotenv()`.

| Atributo | Variável de Ambiente | Valor Padrão (Gmail) |
|---|---|---|
| `USER` | `EMAIL_USER` | seu_email@gmail.com |
| `PASS` | `EMAIL_PASS` | App Password de 16 chars |
| `SMTP_SERVER` | `EMAIL_SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `EMAIL_SMTP_PORT` | `587` |

---

## Função `send_email`

### Assinatura

```python
def send_email(to_email: str, subject: str, message_body: str, is_html: bool = False) -> bool
```

### Parâmetros

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `to_email` | `str` | — | Endereço de destino |
| `subject` | `str` | — | Assunto do e-mail |
| `message_body` | `str` | — | Corpo do e-mail |
| `is_html` | `bool` | `False` | Se `True`, envia como `text/html`; caso contrário, `text/plain` |

### Retorno

| Valor | Situação |
|---|---|
| `True` | E-mail enviado com sucesso |
| `False` | Falha (credenciais ausentes, erro SMTP, etc.) |

---

## Fluxo de Envio

```
send_email() chamada
      │
      ├─ Credenciais vazias? → log ERROR, return False
      │
      ├─ Monta MIMEMultipart("alternative")
      │   ├─ Subject, From, To
      │   └─ MIMEText(body, "plain" ou "html")
      │
      └─ smtplib.SMTP(server, port, timeout=15)
              ├─ server.starttls()         ← criptografia TLS
              ├─ server.login(user, pass)
              ├─ server.send_message(msg)
              └─ return True
```

---

## E-mails Enviados pelo Sistema

O `monitor_service` dispara e-mails em três momentos:

### 1. Monitoramento Iniciado

```
Assunto: Monitoramento Iniciado
Corpo:   O monitoramento para a URL https://... foi iniciado com sucesso às 2026-04-15 10:00:00.
```

### 2. Valor Alterado

```
Assunto: Valor alterado!
Corpo:   O valor monitorado foi alterado.

         URL: https://...
         Data: 2026-04-15 10:05:32

         Valor antigo: $74,228.31
         Novo valor: $74,231.83
```

### 3. Monitoramento Finalizado

```
Assunto: Monitoramento Finalizado
Corpo:   O monitoramento para a URL https://... foi encerrado às 2026-04-15 10:30:00.
```

---

## Erros Tratados

| Exceção | Causa | Ação |
|---|---|---|
| Credenciais ausentes | `.env` não configurado | log ERROR, retorna `False` |
| `SMTPAuthenticationError` | Senha errada ou App Password não usada | log ERROR |
| `SMTPConnectError` | Servidor SMTP inacessível | log ERROR |
| `Exception` genérica | Qualquer outro erro de rede/SMTP | log ERROR |

!!! warning "App Password obrigatório"
    O Gmail exige **App Password** para autenticação via SMTP quando a conta usa verificação em duas etapas. A senha normal da conta **não funciona**.

---

## Evolução entre Branches

=== "feat/send-email (versão inicial)"
    ```python
    # Versão simplificada — sem MIMEMultipart, sem tratamento específico de erros
    def send_email(to_email: str, subject: str, message: str):
        msg = MIMEText(message)
        msg["Subject"] = subject
        ...
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
    ```

=== "dev (versão final)"
    ```python
    # Versão robusta — MIMEMultipart, suporte a HTML, tratamento de erros específicos,
    # SMTP server/port configuráveis via .env, retorno booleano
    def send_email(..., is_html: bool = False) -> bool:
        ...
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed...")
        except smtplib.SMTPConnectError:
            logger.error(f"Could not connect to SMTP server...")
    ```
