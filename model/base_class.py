from sqlalchemy.ext.declarative import declarative_base
from base_class import Base
from sqlalchemy import Column, Integer, String
"""
Provides the shared SQLAlchemy declarative base for all ORM (Object-Relational Mapping) model classes.
This module creates and exports a single `Base` object by calling
`sqlalchemy.ext.declarative.declarative_base()`. Import and subclass this
`Base` in the model to define mapped classes (database tables). Using
one central declarative base ensures all models share the same metadata and
can be collectively managed for tasks such as creating tables, running
migrations, and reflecting schema.
Example:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)
"""

Base = declarative_base()