"""Team management service."""

import secrets
from datetime import datetime, timezone
from uuid import UUID

from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.core.security import hash_password
from app.models.team_member import TeamMember
from app.models.user import User
from app.repositories.team_member_repo import TeamMemberRepository
from app.repositories.user_repo import UserRepository
from app.schemas.team import TeamMemberOut, TeamInviteRequest, TeamMemberUpdateRequest


class TeamService:
    def __init__(self, db):
        self.db = db
        self.repo = TeamMemberRepository(db)
        self.user_repo = UserRepository(db)

    def list_members(self, tenant_id: UUID, skip: int = 0, limit: int = 50) -> tuple[list[TeamMemberOut], int]:
        items = self.repo.get_all(tenant_id=tenant_id, skip=skip, limit=limit)
        total = self.repo.count(tenant_id=tenant_id)
        result: list[TeamMemberOut] = []
        for tm in items:
            user = self.user_repo.get_by_id(tm.user_id, tenant_id=tenant_id)
            if not user:
                continue
            result.append(
                TeamMemberOut(
                    id=tm.id,
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    role=tm.role,
                    status=tm.status,
                    invited_at=tm.invited_at,
                    accepted_at=tm.accepted_at,
                )
            )
        return result, total

    def invite_member(self, tenant_id: UUID, payload: TeamInviteRequest) -> TeamMemberOut:
        role = payload.role.upper()
        if role not in ("STAFF", "TENANT_ADMIN"):
            raise BadRequestError("Role must be STAFF or TENANT_ADMIN")
        existing_user = self.user_repo.get_by_email(payload.email)
        if existing_user and existing_user.tenant_id != tenant_id:
            raise ConflictError("Email already belongs to another tenant")

        if existing_user and self.repo.get_by_user(existing_user.id, tenant_id):
            raise ConflictError("Member already invited")

        user = existing_user
        if not user:
            temp_password = f"Tmp@{secrets.token_urlsafe(8)}"
            user = User(
                tenant_id=tenant_id,
                role=role,
                name=payload.name,
                email=payload.email,
                password_hash=hash_password(temp_password),
                is_verified=False,
            )
            self.db.add(user)
            self.db.flush()

        user.role = role
        tm = TeamMember(
            tenant_id=tenant_id,
            user_id=user.id,
            role=role,
            status="INVITED",
            invited_email=payload.email,
        )
        self.db.add(tm)
        self.db.commit()
        self.db.refresh(tm)
        return TeamMemberOut(
            id=tm.id,
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=tm.role,
            status=tm.status,
            invited_at=tm.invited_at,
            accepted_at=tm.accepted_at,
        )

    def update_member(self, tenant_id: UUID, member_id: UUID, payload: TeamMemberUpdateRequest) -> TeamMemberOut:
        tm = self.repo.get_by_id(member_id, tenant_id=tenant_id)
        if not tm:
            raise NotFoundError("Team member not found")
        user = self.user_repo.get_by_id(tm.user_id, tenant_id=tenant_id)
        if not user:
            raise NotFoundError("User not found")
        if payload.role is not None:
            new_role = payload.role.upper()
            if new_role not in ("STAFF", "TENANT_ADMIN"):
                raise BadRequestError("Role must be STAFF or TENANT_ADMIN")
            tm.role = new_role
            user.role = new_role
        if payload.status is not None:
            tm.status = payload.status.upper()
            if tm.status == "ACTIVE" and tm.accepted_at is None:
                tm.accepted_at = datetime.now(timezone.utc)
        self.db.commit()
        return TeamMemberOut(
            id=tm.id,
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=tm.role,
            status=tm.status,
            invited_at=tm.invited_at,
            accepted_at=tm.accepted_at,
        )

    def delete_member(self, tenant_id: UUID, member_id: UUID) -> None:
        tm = self.repo.get_by_id(member_id, tenant_id=tenant_id)
        if not tm:
            raise NotFoundError("Team member not found")
        self.repo.delete(tm)

