"""
Database initialization for the application.

Creates the local directory for the SQLite file, initializes the SQLAlchemy
engine and session factory, creates the database if missing, and ensures all
tables defined on the Base metadata exist.
"""

import os
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import model definitions
from model.base_class import Base
from model.hydrogen_generator import HydrogenGenerator
from model.customer import Customer

# Directory where the SQLite database file will be stored
DB_DIR = "database"

# Ensure the database directory exists
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

# SQLite database URL (local file)
DB_URL = f"sqlite:///{DB_DIR}/db.sqlite3"

# Create the SQLAlchemy engine
engine = create_engine(DB_URL, echo=False)

# Session factory for creating new Session objects
session_factory = sessionmaker(bind=engine)

# Create the database if it does not exist
if not database_exists(engine.url):
    create_database(engine.url)

# Create all tables defined on the Base metadata (if missing)
Base.metadata.create_all(engine)