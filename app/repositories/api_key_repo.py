"""API key repository."""

from sqlalchemy.orm import Session

from app.models.api_key import ApiKey
from app.repositories.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    def __init__(self, db: Session):
        super().__init__(ApiKey, db)

