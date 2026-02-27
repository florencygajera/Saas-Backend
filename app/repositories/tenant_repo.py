"""
Tenant repository.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    def __init__(self, db: Session):
        super().__init__(Tenant, db)

    def get_all_tenants(self, skip: int = 0, limit: int = 50) -> List[Tenant]:
        return self.db.query(Tenant).offset(skip).limit(limit).all()

    def count_all(self) -> int:
        return self.db.query(Tenant).count()

    def get_by_id_no_filter(self, tenant_id: UUID) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
