from typing import List

from pydantic import BaseModel



class HydrogenGeneratorBaseSchema(BaseModel):
    """Shared generator fields."""

    generator_id: int
    serial_number: str
    acquisition_type: str
    stack_type: str
    number_of_cells: int
    stack_voltage: float
    current_density: float


class HydrogenGeneratorSchema(HydrogenGeneratorBaseSchema):
    """Payload for creating/updating a generator."""


class HydrogenGeneratorViewSchema(HydrogenGeneratorBaseSchema):
    """Payload returned when reading generator data."""


class HydrogenGeneratorSearchSchema(BaseModel):
    """Schema used to query a specific generator by its serial number."""

    serial_number: str = "H2-PROTO-001"


class HydrogenGeneratorListSchema(BaseModel):
    """Returns a list of all generators currently in the system."""

    generators: List[HydrogenGeneratorViewSchema]


class HydrogenGeneratorDeleteSchema(BaseModel):
    """Used to confirm which generator was successfully removed."""

    message: str
    serial_number: str