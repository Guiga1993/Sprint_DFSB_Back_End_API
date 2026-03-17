from typing import Any, List, Literal
import re

from pydantic import BaseModel, Field, field_validator

# Allowed dropdown values — must match the <select> options in the frontend.
AcquisitionType = Literal["Leasing", "Renting", "Direct Sales"]
StackType = Literal["PEMFC", "Alcaline", "SOFC", "AEMFC", "Other/Personalized"]
# Fixed serial format expected by backend and frontend validations.
SERIAL_NUMBER_REGEX = r"GEN-\d{4}"
# Legacy serial formats accepted for lookup/delete compatibility.
SERIAL_LOOKUP_REGEX = r"(?:GEN-\d{4}|GENSET-\d{4})"


# ---------- Input Schema ----------
# Validates the request body when creating a new generator (POST /hydrogen-generator).
class HydrogenGeneratorCreateSchema(BaseModel):
    # Unique identifier; stripped and uppercased (max 50 chars, matches DB column).
    serial_number: str
    # Must be one of the pre-defined dropdown values from the frontend.
    acquisition_type: AcquisitionType
    # Must be one of the pre-defined stack technology options.
    stack_type: StackType
    # Physical constraints: at least 1 cell, reasonable upper bound.
    number_of_cells: int = Field(gt=0, le=5000)
    # Voltage in volts; must be positive with a sensible ceiling.
    stack_voltage: float = Field(gt=0, le=2000)
    # Current density in A/cm²; must be positive.
    current_density: float = Field(gt=0, le=5000)

    @field_validator("serial_number")
    @classmethod
    def validate_serial_number(cls, value: str) -> str:
        """Normalize serial and validate required GEN-0000 format + length."""
        normalized = value.strip().upper()
        # Step 1: reject empty values.
        if not normalized:
            raise ValueError("O número de série não pode estar vazio.")
        # Step 2: enforce fixed format required by the project.
        if not re.fullmatch(SERIAL_NUMBER_REGEX, normalized):
            raise ValueError("O número de série deve seguir o formato GEN-0000 (ex: GEN-0001).")
        # Step 3: keep compatibility with DB column size.
        if len(normalized) > 50:
            raise ValueError("O número de série deve ter no máximo 50 caracteres.")
        return normalized


# ---------- Query Schema ----------
# Validates the query parameter used to fetch or delete a single generator.
class HydrogenGeneratorSearchSchema(BaseModel):
    # Serial number to look up; stripped and uppercased for consistent DB matching.
    serial_number: str = Field(default="GEN-0001")

    @field_validator("serial_number")
    @classmethod
    def validate_search_serial_number(cls, value: str) -> str:
        """Normalize serial and validate accepted lookup formats + length."""
        normalized = value.strip().upper()
        # Step 1: reject empty values.
        if not normalized:
            raise ValueError("O número de série não pode estar vazio.")
        # Step 2: accept current and legacy serial formats for searches/deletes.
        if not re.fullmatch(SERIAL_LOOKUP_REGEX, normalized):
            raise ValueError("O número de série deve seguir o formato GEN-0000 (ex: GEN-0001).")
        # Step 3: keep compatibility with DB column size.
        if len(normalized) > 50:
            raise ValueError("O número de série deve ter no máximo 50 caracteres.")
        return normalized


# ---------- Response Schemas ----------
# Describes the JSON shape returned when reading generator data from the database.
class HydrogenGeneratorViewSchema(BaseModel):
    generator_id: int
    serial_number: str
    acquisition_type: str
    stack_type: str
    number_of_cells: int
    stack_voltage: float
    current_density: float


# Wraps a list of HydrogenGeneratorViewSchema for the GET /hydrogen-generators endpoint.
class HydrogenGeneratorListSchema(BaseModel):
    generators: List[HydrogenGeneratorViewSchema]


# Returned after a successful DELETE /hydrogen-generator operation.
class HydrogenGeneratorDeleteSchema(BaseModel):
    message: str
    serial_number: str


# ---------- Serialization Helpers ----------
# Converts a HydrogenGenerator ORM object into a plain dict for JSON responses.
def get_hydrogen_generator(generator: Any) -> dict[str, Any]:
    return {
        "generator_id": generator.generator_id,
        "serial_number": generator.serial_number,
        "acquisition_type": generator.acquisition_type,
        "stack_type": generator.stack_type,
        "number_of_cells": generator.number_of_cells,
        "stack_voltage": generator.stack_voltage,
        "current_density": generator.current_density,
    }


# Converts a list of HydrogenGenerator ORM objects into the shape expected by HydrogenGeneratorListSchema.
def get_hydrogen_generators(generators: list[Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "generators": [
            {
                "generator_id": generator.generator_id,
                "serial_number": generator.serial_number,
                "acquisition_type": generator.acquisition_type,
                "stack_type": generator.stack_type,
                "number_of_cells": generator.number_of_cells,
                "stack_voltage": generator.stack_voltage,
                "current_density": generator.current_density,
            }
            for generator in generators
        ]
    }