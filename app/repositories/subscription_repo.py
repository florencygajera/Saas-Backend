"""
Subscription repository.
"""

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.repositories.base import BaseRepository


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, db: Session):
        super().__init__(Subscription, db)

    def get_by_tenant(self, tenant_id: UUID) -> List[Subscription]:
        return (
            self.db.query(Subscription)
            .filter(Subscription.tenant_id == tenant_id)
            .order_by(Subscription.created_at.desc())
            .all()
        )
