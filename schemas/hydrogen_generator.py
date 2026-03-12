# pydantic provides BaseModel for data validation/serialization
# and Field for adding metadata, defaults and validation rules.
from pydantic import BaseModel, Field

# typing supplies type hints like Optional and List used in the schemas.
from typing import Optional, List

# datetime is used for timestamp fields (e.g., activation_date).
from datetime import datetime

from model.hydrogen_generator import HydrogenGenerator

class HydrogenGeneratorSchema(BaseModel):
    """ 
    Defines the data required to register/create a new unit.
    Used for POST requests.
    """
    serial_number: str = Field(..., description="Unique hardware serial number", example="H2-PROTO-001")
    model_type: str = Field("Standard", description="The model or version of the generator")
    customer_id: int = Field(..., description="The ID of the customer who owns this unit")

class HydrogenGeneratorViewSchema(BaseModel):
    """ 
    Defines how the generator data will be formatted when sent to the dashboard.
    """
    id: int
    serial_number: str
    model_type: str
    activation_date: datetime
    customer_id: int

class HydrogenGeneratorSearchSchema(BaseModel):
    """ 
    Schema used to query a specific generator by its serial number.
    """
    serial_number: str = "H2-PROTO-001"

class HydrogenGeneratorListSchema(BaseModel):
    """ 
    Returns a list of all generators currently in the system.
    """
    generators: List[HydrogenGeneratorViewSchema]

class HydrogenGeneratorDeleteSchema(BaseModel):
    """ 
    Used to confirm which generator was successfully removed.
    """
    message: str
    serial_number: str