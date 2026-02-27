"""
Staff repository.
"""

from sqlalchemy.orm import Session

from app.models.staff import Staff
from app.repositories.base import BaseRepository


class StaffRepository(BaseRepository[Staff]):
    def __init__(self, db: Session):
        super().__init__(Staff, db)
