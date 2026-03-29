"""Preference repository."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.preference import Preference
from app.repositories.base import BaseRepository


class PreferenceRepository(BaseRepository[Preference]):
    def __init__(self, db: Session):
        super().__init__(Preference, db)

    def get_by_user_id(self, user_id: UUID) -> Preference | None:
        return self.db.query(Preference).filter(Preference.user_id == user_id).first()

