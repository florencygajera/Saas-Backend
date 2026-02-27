"""
Service repository.
"""

from sqlalchemy.orm import Session

from app.models.service import Service
from app.repositories.base import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, db: Session):
        super().__init__(Service, db)
