"""
Service management service (CRUD for tenant-scoped services).
"""

from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.service import Service
from app.repositories.service_repo import ServiceRepository
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceOut


class ServiceService:
    def __init__(self, db: Session):
        self.repo = ServiceRepository(db)
        self.db = db

    def create(self, tenant_id: UUID, payload: ServiceCreate) -> ServiceOut:
        svc = Service(
            tenant_id=tenant_id,
            name=payload.name,
            duration_min=payload.duration_min,
            price=payload.price,
        )
        svc = self.repo.create(svc)
        return ServiceOut.model_validate(svc)

    def list(self, tenant_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[List[ServiceOut], int]:
        items = self.repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.repo.count(tenant_id=tenant_id)
        return [ServiceOut.model_validate(s) for s in items], total

    def get(self, service_id: UUID, tenant_id: UUID) -> ServiceOut:
        svc = self.repo.get_by_id(service_id, tenant_id=tenant_id)
        if not svc:
            raise NotFoundError("Service not found")
        return ServiceOut.model_validate(svc)

    def update(self, service_id: UUID, tenant_id: UUID, payload: ServiceUpdate) -> ServiceOut:
        svc = self.repo.get_by_id(service_id, tenant_id=tenant_id)
        if not svc:
            raise NotFoundError("Service not found")
        if payload.name is not None:
            svc.name = payload.name
        if payload.duration_min is not None:
            svc.duration_min = payload.duration_min
        if payload.price is not None:
            svc.price = payload.price
        if payload.is_active is not None:
            svc.is_active = payload.is_active
        svc = self.repo.update(svc)
        return ServiceOut.model_validate(svc)

    def delete(self, service_id: UUID, tenant_id: UUID) -> None:
        svc = self.repo.get_by_id(service_id, tenant_id=tenant_id)
        if not svc:
            raise NotFoundError("Service not found")
        self.repo.delete(svc)
