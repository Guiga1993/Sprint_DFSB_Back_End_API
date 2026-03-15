from typing import Any, List

from pydantic import BaseModel, EmailStr


class CustomerSchema(BaseModel):
    """Define os dados esperados para criação/edição de um customer."""

    name: str
    email: EmailStr
    tx_id: str


class CustomerSearchSchema(BaseModel):
    """Define os campos para busca de um customer por ID."""

    customer_id: int = 1


class CustomerViewSchema(BaseModel):
    """Define a estrutura de retorno de um customer."""

    customer_id: int
    name: str
    email: str
    tx_id: str


class CustomerListSchema(BaseModel):
    """Define a estrutura de retorno para listagem de customers."""

    customers: List[CustomerViewSchema]


class CustomerDeleteSchema(BaseModel):
    """Define a estrutura de confirmação de remoção de customer."""

    message: str
    customer_id: int


def apresenta_customer(customer: Any) -> dict[str, Any]:
    """Retorna a representação de um customer."""

    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "email": customer.email,
        "tx_id": customer.tx_id,
    }


def apresenta_customers(customers: list[Any]) -> dict[str, list[dict[str, Any]]]:
    """Retorna a representação de uma lista de customers."""

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