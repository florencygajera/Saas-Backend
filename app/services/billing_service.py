"""Billing service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import desc

from app.core.config import settings
from app.core.exceptions import NotFoundError, BadRequestError
from app.models.subscription import Subscription
from app.repositories.payment_repo import PaymentRepository
from app.repositories.subscription_repo import SubscriptionRepository
from app.repositories.tenant_repo import TenantRepository
from app.schemas.billing import PlanOut, InvoiceItem


PLAN_CATALOG = {
    "basic": PlanOut(
        code="basic",
        name="Basic",
        price=29.0,
        features=["Core bookings", "Basic analytics"],
    ),
    "pro": PlanOut(
        code="pro",
        name="Pro",
        price=79.0,
        features=["Advanced analytics", "Team management", "API access"],
    ),
    "enterprise": PlanOut(
        code="enterprise",
        name="Enterprise",
        price=199.0,
        features=["Unlimited staff", "Priority support", "Custom onboarding"],
    ),
}


class BillingService:
    def __init__(self, db):
        self.db = db
        self.sub_repo = SubscriptionRepository(db)
        self.tenant_repo = TenantRepository(db)
        self.payment_repo = PaymentRepository(db)

    def get_plans(self) -> list[PlanOut]:
        return list(PLAN_CATALOG.values())

    def get_current_subscription(self, tenant_id: UUID) -> Subscription:
        sub = (
            self.db.query(Subscription)
            .filter(Subscription.tenant_id == tenant_id)
            .order_by(desc(Subscription.created_at))
            .first()
        )
        if not sub:
            raise NotFoundError("No subscription found for tenant")
        return sub

    def change_plan(self, tenant_id: UUID, plan: str) -> Subscription:
        plan_key = plan.lower()
        if plan_key not in PLAN_CATALOG:
            raise BadRequestError("Unknown plan")
        tenant = self.tenant_repo.get_by_id_no_filter(tenant_id)
        if not tenant:
            raise NotFoundError("Tenant not found")

        current = (
            self.db.query(Subscription)
            .filter(Subscription.tenant_id == tenant_id, Subscription.status == "active")
            .order_by(desc(Subscription.created_at))
            .first()
        )
        if current:
            current.status = "cancelled"
            current.end_at = datetime.now(timezone.utc)

        selected = PLAN_CATALOG[plan_key]
        sub = Subscription(
            tenant_id=tenant_id,
            plan=selected.code,
            price=selected.price,
            status="active",
        )
        self.db.add(sub)
        tenant.plan = selected.code
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def get_portal_link(self, tenant_id: UUID) -> str:
        return f"{settings.BILLING_PORTAL_BASE_URL.rstrip('/')}/portal/{tenant_id}"

    def list_invoices(self, tenant_id: UUID, skip: int = 0, limit: int = 50) -> tuple[list[InvoiceItem], int]:
        rows, total = self.payment_repo.list_transactions(
            tenant_id=tenant_id, skip=skip, limit=limit
        )
        items = [
            InvoiceItem(
                payment_id=p.id,
                appointment_id=a.id,
                amount=float(p.amount),
                currency=p.currency,
                status=p.status,
                created_at=p.created_at,
                customer_name=c.name,
            )
            for (p, a, c, s) in rows
        ]
        return items, total
