"""
This module initializes the application's database using SQLAlchemy.
Key responsibilities:
- Ensures the existence of a local directory for storing the SQLite database file.
- Configures the SQLAlchemy engine and session factory for database connections.
- Checks for the existence of the database file and creates it if missing.
- Imports all model classes so their tables are registered with SQLAlchemy's Base metadata.
- Automatically creates all tables defined in the model metadata if they do not already exist in the database.
Exports:
- Base: The declarative base class for all models.
- Customer, CustomerGeneratorAsset, HydrogenGenerator: Model classes representing database tables.
- engine: The shared SQLAlchemy engine instance.
- session_factory: Factory for creating new database sessions.

"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from model.base_class import Base
from model.customer import Customer
from model.customer_generator_asset import CustomerGeneratorAsset
from model.hydrogen_generator import HydrogenGenerator

# Import model classes so SQLAlchemy registers their tables in Base.metadata.

DB_DIR = "database"

if not os.path.exists(DB_DIR):
    # Create the local folder used to store the SQLite database file.
    os.makedirs(DB_DIR, exist_ok=True)

# SQLite database path stored inside the project database directory.
DB_URL = f"sqlite:///{DB_DIR}/db.sqlite3"

# Shared engine used by the application to connect to the database.
engine = create_engine(DB_URL, echo=False)

# Factory for creating new database sessions when handling requests.
session_factory = sessionmaker(bind=engine)

# Create the database file if it does not exist yet.
if not database_exists(engine.url):
    create_database(engine.url)

# Create all mapped tables that are not yet present in the database.
Base.metadata.create_all(engine)

__all__ = [
    "Base",
    "Customer",
    "CustomerGeneratorAsset",
    "HydrogenGenerator",
]