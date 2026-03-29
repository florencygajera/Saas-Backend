"""Email delivery service for OTP notifications."""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

from app.core.config import settings


class EmailService:
    async def send_otp_email(self, to_email: str, otp: str, purpose: str) -> None:
        if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            return

        subject = "Your OTP Code"
        body = (
            f"Your OTP for {purpose.replace('_', ' ').lower()} is: {otp}. "
            "It expires in 10 minutes."
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.set_content(body)

        await asyncio.to_thread(self._send, msg)

    def _send(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
