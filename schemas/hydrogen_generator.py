from typing import List

from pydantic import BaseModel



# Defines shared fields for hydrogen generator payloads.
class HydrogenGeneratorBaseSchema(BaseModel):

    generator_id: int
    serial_number: str
    acquisition_type: str
    stack_type: str
    number_of_cells: int
    stack_voltage: float
    current_density: float


 # Defines the payload for creating/updating a generator.
class HydrogenGeneratorSchema(HydrogenGeneratorBaseSchema):
    pass


 # Defines the payload returned when reading generator data.
class HydrogenGeneratorViewSchema(HydrogenGeneratorBaseSchema):
    pass


# Defines fields used to query a specific generator by serial number.
class HydrogenGeneratorSearchSchema(BaseModel):

    serial_number: str = "H2-PROTO-001"


# Defines the response structure for listing generators.
class HydrogenGeneratorListSchema(BaseModel):

    generators: List[HydrogenGeneratorViewSchema]


# Defines the confirmation response structure for generator deletion.
class HydrogenGeneratorDeleteSchema(BaseModel):

    message: str
    serial_number: str