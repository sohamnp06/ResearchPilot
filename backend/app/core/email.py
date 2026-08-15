from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_verification_email(
    email: str,
    verification_code: str,
    verification_expires
):
    message = MessageSchema(
        subject="Research Paper Assistant - Email Verification",
        recipients=[email],
        body=f"""
Hello,

Your verification code for Research Paper Assistant is:

🔐 {verification_code}

⏱️ This code is valid for 10 minutes.

Expires at:
{verification_expires.strftime("%H:%M UTC")}

Please verify your email before the code expires.

If you did not create this account, you can ignore this email.

Regards,
Research Paper Assistant
""",
        subtype="plain",
    )

    fast_mail = FastMail(conf)

    await fast_mail.send_message(message)