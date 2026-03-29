"""Team management schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TeamMemberOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    email: EmailStr
    role: str
    status: str
    invited_at: datetime
    accepted_at: Optional[datetime] = None


class TeamInviteRequest(BaseModel):
    name: str
    email: EmailStr
    role: str = "STAFF"


class TeamMemberUpdateRequest(BaseModel):
    role: Optional[str] = None
    status: Optional[str] = None

