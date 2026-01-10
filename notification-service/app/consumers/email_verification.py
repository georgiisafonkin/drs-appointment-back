from jinja2 import Environment, FileSystemLoader
from app.schemas.events import EmailVerificationEvent
from app.core.smtp import send_email
from app.core.config import settings

env = Environment(
    loader=FileSystemLoader("app/templates")
)

template = env.get_template("verify_email.html")

async def handle_email_verification(payload: dict):
    event = EmailVerificationEvent(**payload)

    link = f"{settings.FRONTEND_BASE_URL}/verify-email?token={event.token}"

    html = template.render(link=link)

    await send_email(
        to=event.email,
        subject="Verify your email",
        html_body=html
    )
