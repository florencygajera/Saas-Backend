"""OTP token repository."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.otp_token import OtpToken
from app.repositories.base import BaseRepository


class OtpTokenRepository(BaseRepository[OtpToken]):
    def __init__(self, db: Session):
        super().__init__(OtpToken, db)

    def get_valid_token(
        self, user_id: UUID, purpose: str, token_hash: str
    ) -> Optional[OtpToken]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(OtpToken)
            .filter(
                OtpToken.user_id == user_id,
                OtpToken.purpose == purpose,
                OtpToken.token_hash == token_hash,
                OtpToken.used_at.is_(None),
                OtpToken.expires_at > now,
            )
            .order_by(OtpToken.created_at.desc())
            .first()
        )

    def mark_previous_tokens_used(self, user_id: UUID, purpose: str) -> None:
        now = datetime.now(timezone.utc)
        (
            self.db.query(OtpToken)
            .filter(
                OtpToken.user_id == user_id,
                OtpToken.purpose == purpose,
                OtpToken.used_at.is_(None),
            )
            .update({"used_at": now})
        )
        self.db.flush()
