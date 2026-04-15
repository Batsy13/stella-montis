import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText

load_dotenv()

def send_email(to_email: str, subject: str, message: str):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Erro ao enviar email: {e}")