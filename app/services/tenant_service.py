"""
Tenant service — provisioning, enable/disable, listing.
"""

import secrets
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ConflictError
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.user import User
from app.models.subscription import Subscription
from app.repositories.tenant_repo import TenantRepository
from app.repositories.user_repo import UserRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.schemas.tenant import (
    TenantCreate,
    TenantOut,
    TenantProvisionResponse,
    TenantUpdate,
)


class TenantService:
    def __init__(self, db: Session):
        self.db = db
        self.tenant_repo = TenantRepository(db)
        self.user_repo = UserRepository(db)
        self.sub_repo = SubscriptionRepository(db)

    def provision_tenant(self, payload: TenantCreate) -> TenantProvisionResponse:
        """Create tenant + tenant admin + initial subscription in one transaction."""
        # Check email uniqueness
        existing = self.user_repo.get_by_email(payload.admin_email)
        if existing:
            raise ConflictError(f"Email {payload.admin_email} already registered")

        # Create tenant
        tenant = Tenant(name=payload.name, plan=payload.plan)
        self.db.add(tenant)
        self.db.flush()  # get tenant.id

        # Generate temp password
        temp_password = "Admin@123"  # deterministic for demo; use secrets in prod

        # Create tenant admin
        admin = User(
            tenant_id=tenant.id,
            role="TENANT_ADMIN",
            name=payload.admin_name,
            email=payload.admin_email,
            password_hash=hash_password(temp_password),
        )
        self.db.add(admin)

        # Create subscription
        sub = Subscription(
            tenant_id=tenant.id,
            plan=payload.plan,
            price=payload.subscription_price,
            status="active",
        )
        self.db.add(sub)

        self.db.commit()
        self.db.refresh(tenant)

        return TenantProvisionResponse(
            tenant=TenantOut.model_validate(tenant),
            admin_email=payload.admin_email,
            admin_temp_password=temp_password,
        )

    def list_tenants(self, skip: int = 0, limit: int = 50):
        tenants = self.tenant_repo.get_all_tenants(skip=skip, limit=limit)
        total = self.tenant_repo.count_all()
        return tenants, total

    def update_tenant(self, tenant_id: UUID, payload: TenantUpdate) -> TenantOut:
        tenant = self.tenant_repo.get_by_id_no_filter(tenant_id)
        if not tenant:
            raise NotFoundError("Tenant not found")

        if payload.is_active is not None:
            tenant.is_active = payload.is_active
        if payload.name is not None:
            tenant.name = payload.name
        if payload.plan is not None:
            tenant.plan = payload.plan

        self.db.commit()
        self.db.refresh(tenant)
        return TenantOut.model_validate(tenant)

    def get_tenant(self, tenant_id: UUID) -> TenantOut:
        tenant = self.tenant_repo.get_by_id_no_filter(tenant_id)
        if not tenant:
            raise NotFoundError("Tenant not found")
        return TenantOut.model_validate(tenant)
