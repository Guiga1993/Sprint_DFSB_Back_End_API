from typing import Annotated, Any, List
import re

from pydantic import BaseModel, EmailStr, Field, StringConstraints, field_validator

# Reusable type alias: enforces name length between 2 and 150 characters,
# matching the database column constraint (String(150)).
NonEmptyName = Annotated[str, StringConstraints(min_length=2, max_length=150)]
# Fixed tax ID format expected by backend and frontend validations.
TAX_ID_REGEX = r"\d{3}-\d{2}-\d{4}"


# ---------- Input Schema ----------
# Validates the request body when creating a new customer (POST /customer).
class CustomerSchema(BaseModel):
    # Must be 2-150 chars; whitespace-only values are rejected by the validator below.
    name: NonEmptyName
    # Pydantic EmailStr validates RFC-compliant email format automatically.
    email: EmailStr
    # Fiscal identifier; must follow the format 000-00-0000 (digits and dashes).
    tx_id: str = Field(min_length=11, max_length=11)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Normalize name and validate non-empty + minimum length."""
        normalized = value.strip()
        # Step 1: reject empty values after trimming.
        if not normalized:
            raise ValueError("O nome não pode estar vazio.")
        # Step 2: enforce minimum length required by the project.
        if len(normalized) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")
        return normalized

    @field_validator("tx_id")
    @classmethod
    def validate_tx_id(cls, value: str) -> str:
        """Validate Tax ID against the required format: 000-00-0000."""
        # Tax ID must match the fixed pattern used across frontend/backend.
        if not re.fullmatch(TAX_ID_REGEX, value):
            raise ValueError("O Tax ID deve seguir o formato 000-00-0000.")
        return value


# ---------- Query Schema ----------
# Validates the query parameter used to fetch or delete a single customer.
class CustomerSearchSchema(BaseModel):
    # Must be a positive integer referencing an existing customer PK.
    customer_id: int = Field(default=1, gt=0)


# ---------- Response Schemas ----------
# Describes the JSON shape returned for a single customer.
class CustomerViewSchema(BaseModel):
    customer_id: int
    name: str
    email: str
    tx_id: str


# Wraps a list of CustomerViewSchema for the GET /customers endpoint.
class CustomerListSchema(BaseModel):
    customers: List[CustomerViewSchema]


# Returned after a successful DELETE /customer operation.
class CustomerDeleteSchema(BaseModel):
    message: str
    customer_id: int


# ---------- Serialization Helpers ----------
# Converts a Customer ORM object into a plain dict for JSON responses.
def get_customer(customer: Any) -> dict[str, Any]:
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "tx_id": customer.tx_id,
    }


# Converts a list of Customer ORM objects into the shape expected by CustomerListSchema.
def get_customers(customers: list[Any]) -> dict[str, list[dict[str, Any]]]:
    result: list[dict[str, Any]] = []
    for customer in customers:
        result.append(
            {
                "customer_id": customer.customer_id,
                "name": customer.name,
                "email": customer.email,
                "tx_id": customer.tx_id,
            }
        )

    return {"customers": result}