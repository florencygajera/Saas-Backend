"""
Base repository with tenant-scoped query helpers.
"""

from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository that enforces tenant_id filtering for all queries.
    SUPER_ADMIN bypasses tenant filter by passing tenant_id=None.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def _base_query(self, tenant_id: Optional[UUID] = None):
        """Return a query filtered by tenant_id when provided."""
        q = self.db.query(self.model)
        if tenant_id is not None and hasattr(self.model, "tenant_id"):
            q = q.filter(self.model.tenant_id == tenant_id)  # type: ignore
        return q

    def get_by_id(self, id: UUID, tenant_id: Optional[UUID] = None) -> Optional[ModelType]:
        return self._base_query(tenant_id).filter(self.model.id == id).first()  # type: ignore

    def get_all(
        self,
        tenant_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ModelType]:
        return self._base_query(tenant_id).offset(skip).limit(limit).all()

    def count(self, tenant_id: Optional[UUID] = None) -> int:
        return self._base_query(tenant_id).count()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        self.db.delete(obj)
        self.db.commit()
