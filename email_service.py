import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, message: str):
    sender_email = "stella.montis.aa@gmail.com"
    password = "yvsa plid txdy yqqm"

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