"""
Customer repository.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: Session):
        super().__init__(Customer, db)

    def get_by_user_id(self, user_id: UUID, tenant_id: UUID) -> Optional[Customer]:
        return (
            self.db.query(Customer)
            .filter(
                Customer.user_id == user_id,
                Customer.tenant_id == tenant_id,
            )
            .first()
        )
