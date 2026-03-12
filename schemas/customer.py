from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
# We import the Generator schema to show nested data in the view
from schemas.hydrogen_generator import HydrogenGeneratorViewSchema

class CustomerSchema(BaseModel):
    """ Defines how a new customer should be represented/created for creation.
    """
    name: str = Field(..., example="H2 Energy Corp")
    email: EmailStr = Field(..., example="contact@h2energy.com")
    tax_id: Optional[str] = Field(None, example="12-3456789")

class CustomerSearchSchema(BaseModel):
    """ Used to find a customer by their unique email.
    """
    name: str = "H2 Energy Corp"

class CustomerViewSchema(BaseModel):
    """ Defines the structure for returning customer data.
    """
    id: int = 1
    name: str
    email: str
    tax_id: Optional[str]
    registration_date: datetime

class CustomerFullViewSchema(CustomerViewSchema):
    """ 
    A 'Deep' schema that includes all generators owned by the customer.
    """
    generators: List[HydrogenGeneratorViewSchema] = []

class CustomerListSchema(BaseModel):
    """ Returns a list of all customers.
    """
    customers: List[CustomerViewSchema]