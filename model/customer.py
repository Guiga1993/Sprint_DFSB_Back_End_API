from sqlalchemy import Column, String, Integer, DateTime  # Column defines table fields; String/Integer/DateTime are SQL types
from sqlalchemy.orm import relationship  # relationship declares ORM relationships between models
from datetime import datetime  # datetime used for timestamps/defaults
from model import Base # Base is the declarative base class for ORM models
                               

class Customer(Base):
    """Represents a customer (company or individual) that may own hydrogen generators."""

    __tablename__ = 'customers'  # Name of the database table for this model

    # Primary key for this table
    id = Column("pk_customer", Integer, primary_key=True) 

    # Basic contact fields
    name = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    tax_id = Column(String(20), unique=True)  # e.g. SSN, EIN, CNPJ

    # Registration timestamp.
    # Note: using datetime.now() with parentheses evaluates once at import time.
    # Prefer passing the callable (datetime.utcnow) or using SQLAlchemy's server_default.
    registration_date = Column(DateTime, default=datetime.now())

    # One-to-many ORM relationship: a Customer can own multiple HydrogenGenerator objects.
    # - Uses the class name string to avoid circular imports between models.
    # - back_populates keeps the bidirectional attribute (HydrogenGenerator.customer) in sync.
    # - cascade="all, delete-orphan" propagates persistence operations (insert/update/delete/etc.)
    #   to child generators and automatically removes DB rows for generators dropped from this collection.
    # - The attribute is a list-like collection managed by SQLAlchemy.
    generators = relationship(
        "HydrogenGenerator",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    def __init__(self, name: str, email: str, tax_id: str = None):
        """
        Initialize a Customer instance.

        Args:
            name: Company or individual name.
            email: Primary contact email address.
            tax_id: Optional official tax identifier.
        """
        self.name = name
        self.email = email
        self.tax_id = tax_id

    def add_generator(self, generator):
        """
        Link a HydrogenGenerator to this customer.

        This appends the generator to the relationship collection. If the
        generator object has a 'customer' attribute, SQLAlchemy will keep
        both sides synchronized automatically when the session is flushed.
        """
        self.generators.append(generator)