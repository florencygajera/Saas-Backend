"""
Declarative base and model imports — guarantees all models are loaded
before Alembic or create_all is called.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so that Base.metadata picks them up
from app.models.tenant import Tenant  # noqa: F401, E402
from app.models.subscription import Subscription  # noqa: F401, E402
from app.models.user import User  # noqa: F401, E402
from app.models.service import Service  # noqa: F401, E402
from app.models.staff import Staff  # noqa: F401, E402
from app.models.customer import Customer  # noqa: F401, E402
from app.models.appointment import Appointment  # noqa: F401, E402
from app.models.payment import Payment  # noqa: F401, E402
from app.models.event import Event  # noqa: F401, E402
