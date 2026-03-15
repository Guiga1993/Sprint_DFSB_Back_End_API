from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from model.base_class import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column("pk_customer", Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tx_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    def __init__(self, name: str, email: str, tx_id: str):
        """Cria um Customer.

        Arguments:
            name: nome do cliente.
            email: email do cliente.
            tx_id: identificador fiscal do cliente.
        """
        self.name = name
        self.email = email
        self.tx_id = tx_id