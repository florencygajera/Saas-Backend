"""
Customer management service (CRUD for tenant-scoped customers).
"""

from typing import List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def create(self, tenant_id: UUID, payload: CustomerCreate) -> CustomerOut:
        obj = Customer(
            tenant_id=tenant_id,
            name=payload.name,
            phone=payload.phone,
            email=payload.email,
        )
        obj = self.repo.create(obj)
        return CustomerOut.model_validate(obj)

    def list(
        self, tenant_id: UUID, skip: int = 0, limit: int = 50
    ) -> Tuple[List[CustomerOut], int]:
        items = self.repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.repo.count(tenant_id=tenant_id)
        return [CustomerOut.model_validate(c) for c in items], total

    def get(self, customer_id: UUID, tenant_id: UUID) -> CustomerOut:
        obj = self.repo.get_by_id(customer_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Customer not found")
        return CustomerOut.model_validate(obj)

    def update(
        self, customer_id: UUID, tenant_id: UUID, payload: CustomerUpdate
    ) -> CustomerOut:
        obj = self.repo.get_by_id(customer_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Customer not found")
        if payload.name is not None:
            obj.name = payload.name
        if payload.phone is not None:
            obj.phone = payload.phone
        if payload.email is not None:
            obj.email = payload.email
        obj = self.repo.update(obj)
        return CustomerOut.model_validate(obj)

    def delete(self, customer_id: UUID, tenant_id: UUID) -> None:
        obj = self.repo.get_by_id(customer_id, tenant_id=tenant_id)
        if not obj:
            raise NotFoundError("Customer not found")
        self.repo.delete(obj)
