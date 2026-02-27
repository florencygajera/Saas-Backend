"""
Auth endpoints — login, me.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, CurrentUser
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.schemas.common import SingleResponse
from app.services.auth_service import AuthService
from app.repositories.user_repo import UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(payload)


@router.get("/me", response_model=SingleResponse)
def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user.user_id)
    if not user:
        return SingleResponse(data=None, message="User not found")
    return SingleResponse(data=UserInfo.model_validate(user).model_dump())
