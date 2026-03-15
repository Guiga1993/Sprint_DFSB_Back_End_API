"""
Provides the shared SQLAlchemy declarative base for all ORM model classes.

This module exports a single `Base` class for all mapped models in the
application. Using one central declarative base ensures all models share the
same metadata and can be managed together for table creation and migrations.

Example:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass