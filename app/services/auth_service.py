"""
Auth service — login, token creation.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import verify_password, create_access_token
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = self.user_repo.get_by_email(payload.email)
        if not user:
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        # Update last login
        self.user_repo.update_last_login(user)

        token = create_access_token(
            user_id=user.id,
            role=user.role,
            tenant_id=user.tenant_id,
        )

        return LoginResponse(
            access_token=token,
            user=UserInfo.model_validate(user),
        )
