"""
Email utility for sending verification codes.

If MAIL_USERNAME / MAIL_PASSWORD are not configured, verification codes
are printed to the server logs instead of being emailed. This allows
development without an SMTP server.
"""

import logging

logger = logging.getLogger(__name__)


async def send_verification_email(
    email: str,
    verification_code: str,
    verification_expires,
) -> None:
    """
    Send a verification email.

    Falls back to logging the code when SMTP is not configured.
    """
    from app.core.config import settings

    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        # Development mode: print code to logs
        logger.warning(
            f"[DEV MODE] Email not configured. "
            f"Verification code for {email}: {verification_code} "
            f"(expires: {verification_expires})"
        )
        return

    try:
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

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

        message = MessageSchema(
            subject="ResearchPilot — Email Verification",
            recipients=[email],
            body=f"""Hello,

Your verification code for ResearchPilot is:

🔐 {verification_code}

⏱️ This code is valid for 10 minutes.

Expires at: {verification_expires.strftime("%H:%M UTC")}

Please verify your email before the code expires.

If you did not create this account, you can ignore this email.

Regards,
ResearchPilot
""",
            subtype="plain",
        )

        fast_mail = FastMail(conf)
        await fast_mail.send_message(message)
        logger.info(f"Verification email sent to {email}")

    except ImportError:
        logger.warning(
            f"[DEV MODE] fastapi_mail not installed. "
            f"Verification code for {email}: {verification_code}"
        )
    except Exception as exc:
        logger.error(f"Failed to send verification email to {email}: {exc}")
        logger.warning(
            f"[FALLBACK] Verification code for {email}: {verification_code}"
        )