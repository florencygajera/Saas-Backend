"""
Analytics service — tenant stats + platform stats.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, extract, case, and_
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.payment import Payment
from app.models.service import Service
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.analytics import (
    TenantStats,
    TopServiceItem,
    PlatformStats,
    TopTenantItem,
)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------------------
    # Tenant analytics
    # ----------------------------------------------------------------
    def get_tenant_stats(self, tenant_id: UUID) -> TenantStats:
        # Revenue: sum of PAID payments
        revenue = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.tenant_id == tenant_id, Payment.status == "PAID")
            .scalar()
        )

        # Total bookings
        total_bookings = (
            self.db.query(func.count(Appointment.id))
            .filter(Appointment.tenant_id == tenant_id)
            .scalar()
        )

        # Completed count
        completed_count = (
            self.db.query(func.count(Appointment.id))
            .filter(
                Appointment.tenant_id == tenant_id,
                Appointment.status == "COMPLETED",
            )
            .scalar()
        )

        # Cancelled count
        cancelled_count = (
            self.db.query(func.count(Appointment.id))
            .filter(
                Appointment.tenant_id == tenant_id,
                Appointment.status == "CANCELLED",
            )
            .scalar()
        )

        # Top services by booking count + revenue
        top_services_raw = (
            self.db.query(
                Service.id,
                Service.name,
                func.count(Appointment.id).label("bookings"),
                func.coalesce(
                    func.sum(
                        case(
                            (Payment.status == "PAID", Payment.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("revenue"),
            )
            .outerjoin(Appointment, and_(
                Appointment.service_id == Service.id,
                Appointment.tenant_id == tenant_id,
            ))
            .outerjoin(Payment, and_(
                Payment.appointment_id == Appointment.id,
                Payment.tenant_id == tenant_id,
            ))
            .filter(Service.tenant_id == tenant_id)
            .group_by(Service.id, Service.name)
            .order_by(func.count(Appointment.id).desc())
            .limit(10)
            .all()
        )

        top_services = [
            TopServiceItem(
                service_id=row[0],
                service_name=row[1],
                bookings=row[2],
                revenue=float(row[3]),
            )
            for row in top_services_raw
        ]

        # Heatmap 7x24 — day_of_week (0=Mon..6=Sun) x hour
        heatmap_raw = (
            self.db.query(
                # PostgreSQL: extract DOW returns 0=Sun, 1=Mon, etc.
                # Shift to ISO: 0=Mon ... 6=Sun
                func.mod(
                    (extract("dow", Appointment.start_at) + 6), 7
                ).label("day"),
                extract("hour", Appointment.start_at).label("hour"),
                func.count(Appointment.id).label("cnt"),
            )
            .filter(Appointment.tenant_id == tenant_id)
            .group_by("day", "hour")
            .all()
        )

        heatmap = [[0] * 24 for _ in range(7)]
        for row in heatmap_raw:
            day_idx = int(row[0])
            hour_idx = int(row[1])
            if 0 <= day_idx < 7 and 0 <= hour_idx < 24:
                heatmap[day_idx][hour_idx] = row[2]

        return TenantStats(
            revenue=float(revenue),
            total_bookings=total_bookings,
            completed_count=completed_count,
            cancelled_count=cancelled_count,
            top_services=top_services,
            heatmap_7x24=heatmap,
        )

    # ----------------------------------------------------------------
    # Platform analytics (super admin)
    # ----------------------------------------------------------------
    def get_platform_stats(self) -> PlatformStats:
        # Platform revenue
        platform_revenue = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.status == "PAID")
            .scalar()
        )

        # Total bookings across all tenants
        total_bookings = self.db.query(func.count(Appointment.id)).scalar()

        # Active tenants: had bookings in last 30 days OR user login in last 30 days
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        tenants_with_bookings = (
            self.db.query(Appointment.tenant_id)
            .filter(Appointment.created_at >= cutoff)
            .distinct()
            .subquery()
        )

        tenants_with_logins = (
            self.db.query(User.tenant_id)
            .filter(
                User.last_login_at >= cutoff,
                User.tenant_id.isnot(None),
            )
            .distinct()
            .subquery()
        )

        active_with_bookings = self.db.query(tenants_with_bookings).count()
        active_with_logins = self.db.query(tenants_with_logins).count()

        # Union-like: count distinct tenant_ids from both
        active_tenant_ids = set()
        for (tid,) in self.db.query(tenants_with_bookings):
            if tid:
                active_tenant_ids.add(tid)
        for (tid,) in self.db.query(tenants_with_logins):
            if tid:
                active_tenant_ids.add(tid)
        active_tenants = len(active_tenant_ids)

        # New tenants last 30 days
        new_tenants_last_30d = (
            self.db.query(func.count(Tenant.id))
            .filter(Tenant.created_at >= cutoff)
            .scalar()
        )

        # Top tenants by revenue
        top_tenants_raw = (
            self.db.query(
                Tenant.id,
                Tenant.name,
                func.coalesce(func.sum(Payment.amount), 0).label("rev"),
            )
            .outerjoin(Payment, and_(
                Payment.tenant_id == Tenant.id,
                Payment.status == "PAID",
            ))
            .group_by(Tenant.id, Tenant.name)
            .order_by(func.coalesce(func.sum(Payment.amount), 0).desc())
            .limit(10)
            .all()
        )

        top_tenants = [
            TopTenantItem(
                tenant_id=row[0],
                tenant_name=row[1],
                revenue=float(row[2]),
            )
            for row in top_tenants_raw
        ]

        return PlatformStats(
            platform_revenue=float(platform_revenue),
            total_bookings=total_bookings,
            active_tenants=active_tenants,
            new_tenants_last_30d=new_tenants_last_30d,
            top_tenants_by_revenue=top_tenants,
        )
