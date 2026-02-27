"""
Tenant & subscription schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TenantCreate(BaseModel):
    name: str
    plan: str = "basic"
    admin_name: str
    admin_email: EmailStr
    subscription_price: float = 29.99


class TenantOut(BaseModel):
    id: UUID
    name: str
    plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantProvisionResponse(BaseModel):
    tenant: TenantOut
    admin_email: str
    admin_temp_password: str
    message: str = "Tenant provisioned successfully"


class TenantUpdate(BaseModel):
    is_active: Optional[bool] = None
    name: Optional[str] = None
    plan: Optional[str] = None


class SubscriptionOut(BaseModel):
    id: UUID
    tenant_id: UUID
    plan: str
    price: float
    status: str
    start_at: datetime
    end_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
