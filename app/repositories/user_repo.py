"""
User repository.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def update_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

    def get_by_email_in_tenant(self, email: str, tenant_id: UUID) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email, User.tenant_id == tenant_id)
            .first()
        )
