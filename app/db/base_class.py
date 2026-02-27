"""
Declarative base — model classes import this directly.
Kept separate from model registration to avoid circular imports.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
