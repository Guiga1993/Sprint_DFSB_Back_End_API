from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from model.base_class import Base


# ORM model representing a hydrogen generator unit.
# Maps to the "hydrogen_generators" table in the database.
class HydrogenGenerator(Base):
    __tablename__ = "hydrogen_generators"

    # ---------- Columns ----------
    # Auto-incremented surrogate primary key.
    generator_id: Mapped[int] = mapped_column("pk_generator", Integer, primary_key=True)
    # Unique serial number that identifies the physical unit (max 50 chars).
    serial_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # Acquisition model: Leasing, Renting, or Direct Sales (max 20 chars).
    acquisition_type: Mapped[str] = mapped_column(String(20), nullable=False)
    # Fuel-cell technology: PEMFC, Alcaline, SOFC, AEMFC, or Custom (max 50 chars).
    stack_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Total number of individual cells in the fuel-cell stack.
    number_of_cells: Mapped[int] = mapped_column(Integer, nullable=False)
    # Combined voltage output of the full stack, in volts.
    stack_voltage: Mapped[float] = mapped_column(Float, nullable=False)
    # Operating current density of the stack, in A/cm².
    current_density: Mapped[float] = mapped_column(Float, nullable=False)

    # ---------- Constructor ----------
    def __init__(
        self,
        serial_number: str,
        acquisition_type: str,
        stack_type: str,
        number_of_cells: int,
        stack_voltage: float,
        current_density: float,
    ):
        """Create a new HydrogenGenerator instance.

        Args:
            serial_number: unique identifier for the physical unit.
            acquisition_type: how the generator was acquired.
            stack_type: fuel-cell technology used.
            number_of_cells: cell count in the stack.
            stack_voltage: total voltage output (V).
            current_density: operating current density (A/cm²).
        """
        self.serial_number = serial_number
        self.acquisition_type = acquisition_type
        self.stack_type = stack_type
        self.number_of_cells = number_of_cells
        self.stack_voltage = stack_voltage
        self.current_density = current_density