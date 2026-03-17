from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from model.base_class import Base


# Column-size constraints used in DB mappings.
CUSTOMER_NAME_MAX_LENGTH = 150
CUSTOMER_EMAIL_MAX_LENGTH = 100
CUSTOMER_TAX_ID_MAX_LENGTH = 20


# ORM model representing a customer.
# Maps to the "customers" table in the database.
class Customer(Base):
    __tablename__ = "customers"

    # ---------- Columns ----------
    # Auto-incremented surrogate primary key.
    customer_id: Mapped[int] = mapped_column("pk_customer", Integer, primary_key=True)
    # Full name; max 150 characters, cannot be null.
    name: Mapped[str] = mapped_column(String(CUSTOMER_NAME_MAX_LENGTH), nullable=False)
    # Email address; max 100 characters, must be unique.
    email: Mapped[str] = mapped_column(
        String(CUSTOMER_EMAIL_MAX_LENGTH), unique=True, nullable=False
    )
    # Fiscal identifier (format 000-00-0000); max 20 characters, must be unique.
    tx_id: Mapped[str] = mapped_column(
        String(CUSTOMER_TAX_ID_MAX_LENGTH), unique=True, nullable=False
    )

    # ---------- Constructor ----------

    def __init__(self, name: str, email: str, tx_id: str):
        """Create a new Customer instance.

        Args:
            name: customer's full name.
            email: customer's email address.
            tx_id: customer's fiscal identifier (format 000-00-0000).
        """
        # Step 1: assign core profile fields.
        self.name = name
        self.email = email
        # Step 2: assign external fiscal identifier.
        self.tx_id = tx_id