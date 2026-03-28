"""FastAPI dependencies: DB session, auth extraction, and role guards."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.tenant import Tenant
from app.models.user import User

security_scheme = HTTPBearer()
optional_security_scheme = HTTPBearer(auto_error=False)


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

    # Verify user still exists and is active.
    user = db.query(User).filter(User.id == user_id, User.is_active).first()
    if not user:
        raise UnauthorizedError("User not found or inactive")

    # Enforce tenant is active for tenant-scoped roles.
    if user.role != "SUPER_ADMIN":
        if user.tenant_id is None:
            raise UnauthorizedError("Invalid user tenant mapping")
        tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        if not tenant or not tenant.is_active:
            raise ForbiddenError("Tenant is disabled")

    return CurrentUser(
        user_id=UUID(user_id),
        role=role,
        tenant_id=UUID(tenant_id) if tenant_id else None,
    )


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(optional_security_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser | None:
    if not credentials:
        return None
    try:
        return get_current_user(credentials=credentials, db=db)
    except Exception:
        return None


def require_super_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "SUPER_ADMIN":
        raise ForbiddenError("Super admin access required")
    return current_user


def require_tenant_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "TENANT_ADMIN":
        raise ForbiddenError("Tenant admin access required")
    return current_user


def require_customer(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role != "CUSTOMER":
        raise ForbiddenError("Customer access required")
    return current_user


def require_tenant_admin_or_customer(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if current_user.role not in ("TENANT_ADMIN", "CUSTOMER"):
        raise ForbiddenError("Tenant admin or customer access required")
    return current_user


def require_tenant_scope(current_user: CurrentUser) -> UUID:
    if current_user.tenant_id is None:
        raise ForbiddenError("Tenant-scoped access required")
    return current_user.tenant_id
