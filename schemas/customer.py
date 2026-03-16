from typing import Any, List

from pydantic import BaseModel, EmailStr


# Defines the expected data for customer creation/update.
class CustomerSchema(BaseModel):
    name: str
    email: EmailStr
    tx_id: int


# Defines the fields used to search for a customer by ID.
class CustomerSearchSchema(BaseModel):
    customer_id: int = 1


# Defines the response structure for a customer.
class CustomerViewSchema(BaseModel):
    customer_id: int
    name: str
    email: str
    tx_id: int


# Defines the response structure for listing customers.
class CustomerListSchema(BaseModel):
    customers: List[CustomerViewSchema]


# Defines the confirmation response structure for customer deletion.
class CustomerDeleteSchema(BaseModel):
    message: str
    customer_id: int


# Returns the serialized representation of a customer.
def get_customer(customer: Any) -> dict[str, Any]:
    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "tx_id": customer.tx_id,
    }


# Returns the serialized representation of a customer list.
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


apresenta_customer = get_customer
apresenta_customers = get_customers