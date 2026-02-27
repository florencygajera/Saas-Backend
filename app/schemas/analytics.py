"""
Analytics schemas.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


# ---------- Tenant analytics ----------

class TopServiceItem(BaseModel):
    service_id: UUID
    service_name: str
    bookings: int
    revenue: float


class TenantStats(BaseModel):
    revenue: float
    total_bookings: int
    completed_count: int
    cancelled_count: int
    top_services: List[TopServiceItem]
    heatmap_7x24: List[List[int]]  # 7 rows (Mon-Sun) x 24 cols (hours)


# ---------- Platform analytics ----------

class TopTenantItem(BaseModel):
    tenant_id: UUID
    tenant_name: str
    revenue: float


class PlatformStats(BaseModel):
    platform_revenue: float
    total_bookings: int
    active_tenants: int
    new_tenants_last_30d: int
    top_tenants_by_revenue: List[TopTenantItem]
