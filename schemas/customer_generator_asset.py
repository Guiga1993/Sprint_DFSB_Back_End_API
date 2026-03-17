from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, Field, field_validator


# Domain limits used by both backend and frontend validations.
MAX_GENERATOR_QTD = 10_000


# ---------- Input Schema ----------
# Validates the request body when creating a new customer-generator link.
# installation_date is optional; if omitted, the ORM defaults to datetime.now.
class CustomerGeneratorAssetSchema(BaseModel):
    # Must reference an existing customer PK (positive integer).
    customer_id: int = Field(gt=0)
    # Must reference an existing generator PK (positive integer).
    generator_id: int = Field(gt=0)
    # Number of generator units assigned; between 1 and MAX_GENERATOR_QTD.
    generator_qtd: int = Field(gt=0, le=MAX_GENERATOR_QTD)
    # Optional installation date; must be ISO 8601 format (YYYY-MM-DD).
    installation_date: datetime | None = None

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, value: int) -> int:
        """Ensure customer_id is a positive integer."""
        # customer_id must reference an existing PK (> 0).
        if value <= 0:
            raise ValueError("O ID do cliente deve ser maior que zero.")
        return value

    @field_validator("generator_id")
    @classmethod
    def validate_generator_id(cls, value: int) -> int:
        """Ensure generator_id is a positive integer."""
        # generator_id must reference an existing PK (> 0).
        if value <= 0:
            raise ValueError("O ID do gerador deve ser maior que zero.")
        return value

    @field_validator("generator_qtd")
    @classmethod
    def validate_generator_qtd(cls, value: int) -> int:
        """Ensure generator_qtd stays within accepted project limits."""
        # Step 1: quantity must be greater than zero.
        if value <= 0:
            raise ValueError("A quantidade de geradores deve ser maior que zero.")
        # Step 2: quantity must not exceed MAX_GENERATOR_QTD.
        if value > MAX_GENERATOR_QTD:
            raise ValueError("A quantidade de geradores não pode exceder 10.000.")
        return value


# ---------- Query Schema ----------
# Validates the query parameter used to fetch or delete a single asset link.
class CustomerGeneratorAssetSearchSchema(BaseModel):
    # Must be a positive integer referencing an existing asset PK.
    asset_id: int = Field(default=1, gt=0)


# ---------- Response Schemas ----------
# Describes the JSON shape returned for a single customer-generator asset.
class CustomerGeneratorAssetViewSchema(BaseModel):
    asset_id: int
    customer_id: int
    generator_id: int
    generator_qtd: int
    installation_date: datetime


# Wraps a list of asset links for the listing endpoint.
class CustomerGeneratorAssetListSchema(BaseModel):
    assets: List[CustomerGeneratorAssetViewSchema]


# Returned after a successful delete operation.
class CustomerGeneratorAssetDeleteSchema(BaseModel):
    message: str
    asset_id: int


# ---------- Serialization Helpers ----------
# Converts a CustomerGeneratorAsset ORM object into a plain dict for JSON responses.
def get_asset(asset: Any) -> dict[str, Any]:
    return {
        "asset_id": asset.asset_id,
        "customer_id": asset.customer_id,
        "generator_id": asset.generator_id,
        "generator_qtd": asset.generator_qtd,
        "installation_date": asset.installation_date,
    }


# Converts a list of CustomerGeneratorAsset ORM objects into the shape expected by CustomerGeneratorAssetListSchema.
def get_assets(assets: list[Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "assets": [
            {
                "asset_id": asset.asset_id,
                "customer_id": asset.customer_id,
                "generator_id": asset.generator_id,
                "generator_qtd": asset.generator_qtd,
                "installation_date": asset.installation_date,
            }
            for asset in assets
        ]
    }