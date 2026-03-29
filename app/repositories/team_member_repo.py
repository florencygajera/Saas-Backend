"""Team member repository."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.team_member import TeamMember
from app.repositories.base import BaseRepository


class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self, db: Session):
        super().__init__(TeamMember, db)

    def get_by_user(self, user_id: UUID, tenant_id: UUID) -> TeamMember | None:
        return (
            self.db.query(TeamMember)
            .filter(
                TeamMember.user_id == user_id,
                TeamMember.tenant_id == tenant_id,
            )
            .first()
        )

