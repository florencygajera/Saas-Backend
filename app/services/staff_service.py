"""
Staff management service (CRUD for tenant-scoped staff).
"""

from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.staff import Staff
from app.repositories.staff_repo import StaffRepository
from app.schemas.staff import StaffCreate, StaffUpdate, StaffOut


class StaffService:
    def __init__(self, db: Session):
        self.repo = StaffRepository(db)

    def create(self, tenant_id: UUID, payload: StaffCreate) -> StaffOut:
        obj = Staff(tenant_id=tenant_id, name=payload.name)
        obj = self.repo.create(obj)
        return StaffOut.model_validate(obj)

    def list(
        self, tenant_id: UUID, skip: int = 0, limit: int = 50
    ) -> Tuple[List[StaffOut], int]:
        items = self.repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.repo.count(tenant_id=tenant_id)
        return [StaffOut.model_validate(s) for s in items], total

    def get(self, staff_id: UUID, tenant_id: UUID) -> StaffOut:
        obj = self.repo.get_by_id(staff_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Staff not found")
        return StaffOut.model_validate(obj)

    def update(self, staff_id: UUID, tenant_id: UUID, payload: StaffUpdate) -> StaffOut:
        obj = self.repo.get_by_id(staff_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Staff not found")
        if payload.name is not None:
            obj.name = payload.name
        if payload.is_active is not None:
            obj.is_active = payload.is_active
        obj = self.repo.update(obj)
        return StaffOut.model_validate(obj)

    def delete(self, staff_id: UUID, tenant_id: UUID) -> None:
        obj = self.repo.get_by_id(staff_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Staff not found")
        self.repo.delete(obj)
