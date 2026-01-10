from email.message import EmailMessage
import aiosmtplib
from app.core.config import settings

async def send_email(
    to: str,
    subject: str,
    html_body: str
):
    message = EmailMessage()
    message["From"] = settings.FROM_EMAIL
    message["To"] = to
    message["Subject"] = subject
    message.set_content("HTML email required")
    message.add_alternative(html_body, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=False,
    )
