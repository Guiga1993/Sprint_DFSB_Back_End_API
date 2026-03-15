from datetime import datetime
from typing import List

from pydantic import BaseModel


class CustomerGeneratorAssetBaseSchema(BaseModel):
    """Shared fields for the customer-generator link table."""

    customer_id: int
    generator_id: int
    generaor_qtd: int
    installation_date: datetime


class CustomerGeneratorAssetSchema(BaseModel):
    """Payload used to create/update a customer-generator link."""

    customer_id: int
    generator_id: int
    generaor_qtd: int
    installation_date: datetime | None = None


class CustomerGeneratorAssetViewSchema(CustomerGeneratorAssetBaseSchema):
    """Payload returned when reading a customer-generator link."""

    asset_id: int


class CustomerGeneratorAssetSearchSchema(BaseModel):
    """Schema used to query a specific link by asset ID."""

    asset_id: int = 1


class CustomerGeneratorAssetListSchema(BaseModel):
    """Returns a list of all customer-generator links."""

    assets: List[CustomerGeneratorAssetViewSchema]


class CustomerGeneratorAssetDeleteSchema(BaseModel):
    """Used to confirm which link was successfully removed."""

    message: str
    asset_id: int