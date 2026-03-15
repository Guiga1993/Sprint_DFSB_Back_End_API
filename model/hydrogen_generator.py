from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from model.base_class import Base


class HydrogenGenerator(Base):
    __tablename__ = "hydrogen_generators"

    generator_id: Mapped[int] = mapped_column("pk_generator", Integer, primary_key=True)
    serial_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    acquisition_type: Mapped[str] = mapped_column(String(20), nullable=False)
    stack_type: Mapped[str] = mapped_column(String(50), nullable=False)
    number_of_cells: Mapped[int] = mapped_column(Integer, nullable=False)
    stack_voltage: Mapped[float] = mapped_column(Float, nullable=False)
    current_density: Mapped[float] = mapped_column(Float, nullable=False)

    def __init__(
        self,
        serial_number: str,
        acquisition_type: str,
        stack_type: str,
        number_of_cells: int,
        stack_voltage: float,
        current_density: float,
    ):
        self.serial_number = serial_number
        self.acquisition_type = acquisition_type
        self.stack_type = stack_type
        self.number_of_cells = number_of_cells
        self.stack_voltage = stack_voltage
        self.current_density = current_density