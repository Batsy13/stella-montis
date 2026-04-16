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