"""
FastAPI dependencies: DB session, current user extraction, role guards.
"""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

security_scheme = HTTPBearer()


class CurrentUser:
    """Lightweight container for JWT claims."""

    def __init__(self, user_id: UUID, role: str, tenant_id: Optional[UUID]):
        self.user_id = user_id
        self.role = role
        self.tenant_id = tenant_id


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """Extract and validate JWT, return CurrentUser."""
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise UnauthorizedError("Invalid or expired token")

    user_id = payload.get("sub")
    role = payload.get("role")
    tenant_id = payload.get("tenant_id")

    if not user_id or not role:
        raise UnauthorizedError("Invalid token payload")

    # Verify user still exists and is active
    user = db.query(User).filter(User.id == user_id, User.is_active).first()
    if not user:
        raise UnauthorizedError("User not found or inactive")

    return CurrentUser(
        user_id=UUID(user_id),
        role=role,
        tenant_id=UUID(tenant_id) if tenant_id else None,
    )


def require_super_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "SUPER_ADMIN":
        raise ForbiddenError("Super admin access required")
    return current_user


def require_tenant_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "TENANT_ADMIN":
        raise ForbiddenError("Tenant admin access required")
    return current_user


def require_customer(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if current_user.role != "CUSTOMER":
        raise ForbiddenError("Customer access required")
    return current_user


def require_tenant_admin_or_customer(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role not in ("TENANT_ADMIN", "CUSTOMER"):
        raise ForbiddenError("Tenant admin or customer access required")
    return current_user
