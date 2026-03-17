from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from model.base_class import Base


# ORM model representing the many-to-many relationship between
# customers and hydrogen generators (with quantity and install date).
# Maps to the "customer_generator_assets" table in the database.
class CustomerGeneratorAsset(Base):
    __tablename__ = 'customer_generator_assets'

    # ---------- Columns ----------
    # Auto-incremented surrogate primary key.
    asset_id: Mapped[int] = mapped_column("pk_asset", Integer, primary_key=True)
    # Foreign key referencing the owning customer.
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.pk_customer"), nullable=False)
    # Foreign key referencing the assigned hydrogen generator.
    generator_id: Mapped[int] = mapped_column(Integer, ForeignKey("hydrogen_generators.pk_generator"), nullable=False)
    # Number of generator units assigned in this link.
    generator_qtd: Mapped[int] = mapped_column(Integer, nullable=False)
    # Date the generator(s) were installed; defaults to current timestamp.
    installation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    # ---------- Constructor ----------

    def __init__(
        self,
        customer_id: int,
        generator_id: int,
        generator_qtd: int,
        installation_date: datetime | None = None,
    ):
        """Create a new link between a customer and a hydrogen generator.

        Args:
            customer_id: ID of the linked customer.
            generator_id: ID of the linked generator.
            generator_qtd: number of generator units in this link.
            installation_date: date the generator(s) were installed.
        """
        # Step 1: assign foreign keys and quantity.
        self.customer_id = customer_id
        self.generator_id = generator_id
        self.generator_qtd = generator_qtd

        # Step 2: if provided, override ORM default installation timestamp.
        if installation_date:
            self.installation_date = installation_date
