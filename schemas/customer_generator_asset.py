from datetime import datetime
from typing import Any, List

from pydantic import BaseModel, Field


# ---------- Input Schema ----------
# Validates the request body when creating a new customer-generator link.
# installation_date is optional; if omitted, the ORM defaults to datetime.now.
class CustomerGeneratorAssetSchema(BaseModel):
    # Must reference an existing customer PK (positive integer).
    customer_id: int = Field(gt=0)
    # Must reference an existing generator PK (positive integer).
    generator_id: int = Field(gt=0)
    # Number of generator units assigned; between 1 and 10000.
    generator_qtd: int = Field(gt=0, le=10000)
    # Optional installation date; must be ISO 8601 format (YYYY-MM-DD).
    installation_date: datetime | None = None


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