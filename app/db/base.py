"""
Model registry — imports all models so that Base.metadata picks them up.
Used by Alembic env.py and any code that needs all tables registered.
"""

from app.db.base_class import Base  # noqa: F401

# Import all models so that Base.metadata picks them up
from app.models.tenant import Tenant  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.staff import Staff  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.appointment import Appointment  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.otp_token import OtpToken  # noqa: F401
from app.models.api_key import ApiKey  # noqa: F401
from app.models.team_member import TeamMember  # noqa: F401
from app.models.preference import Preference  # noqa: F401
from app.models.project import Project  # noqa: F401
