from typing import Any
from urllib.parse import unquote

from pydantic import BaseModel
from flask import redirect
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info, Tag  # type: ignore[attr-defined]

from sqlalchemy.exc import IntegrityError

from model import Customer, HydrogenGenerator, session_factory
from schemas.customer import (
    CustomerDeleteSchema,
    CustomerListSchema,
    CustomerSchema,
    CustomerSearchSchema,
    CustomerViewSchema,
    get_customer as serialize_customer,
    get_customers as serialize_customers,
)
from schemas.error import ErrorSchema
from schemas.hydrogen_generator import (
    HydrogenGeneratorDeleteSchema,
    HydrogenGeneratorListSchema,
    HydrogenGeneratorSearchSchema,
    HydrogenGeneratorViewSchema,
)
from schemas.logger import logger


# SQLAlchemy session factory alias used by route handlers.
Session = session_factory

info = Info(title="Hydrogen Generator API", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.json.sort_keys = False  # preserve field order as defined in the dict
CORS(app)

# define swagger ui tags — names and descriptions are visible to the user
home_tag = Tag(
    name="Documentação",
    description=(
        "Redireciona para a página de documentação OpenAPI. "
        "Escolha entre Swagger UI, ReDoc ou RapiDoc para explorar os endpoints."
    ),
)
customer_tag = Tag(
    name="Cliente",
    description="Adição, visualização e remoção de clientes na base de dados",
)
hydrogen_generator_tag = Tag(
    name="Gerador de Hidrogênio",
    description=(
        "Adição, visualização e remoção de geradores de hidrogênio na base de dados"
    ),
)


# Request schema used when creating a hydrogen generator.
class HydrogenGeneratorCreateSchema(BaseModel):
    serial_number: str
    acquisition_type: str
    stack_type: str
    number_of_cells: int
    stack_voltage: float
    current_density: float


# Serialize a HydrogenGenerator ORM object into an API response dict.
def format_hydrogen_generator(generator: Any) -> dict[str, Any]:
    return {
        "generator_id": generator.generator_id,
        "serial_number": generator.serial_number,
        "acquisition_type": generator.acquisition_type,
        "stack_type": generator.stack_type,
        "number_of_cells": generator.number_of_cells,
        "stack_voltage": generator.stack_voltage,
        "current_density": generator.current_density,
    }


# Serialize a list of HydrogenGenerator ORM objects.
def format_hydrogen_generators(
    generators: list[Any]) -> dict[str, list[dict[str, Any]]]:
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


@app.get("/", tags=[home_tag])  # type: ignore
# Redirect root path to the interactive OpenAPI documentation endpoint.
def home():
    """Redireciona para /openapi, com opções de documentação da API."""
    return redirect("/openapi")


@app.post(  # type: ignore[misc]
    "/customer",
    tags=[customer_tag],
    responses={
        "200": CustomerViewSchema,
        "409": ErrorSchema,
        "400": ErrorSchema},
)
# Create a new customer and persist it in the database.
def add_customer(form: CustomerSchema):
    """Adiciona um novo cliente na base de dados."""
    customer = Customer(name=form.name, email=form.email, tx_id=form.tx_id)
    logger.debug("Adding customer with email: '%s'", customer.email)

    try:
        session = Session()
        session.add(customer)
        session.commit()
        logger.debug("Customer added with id: '%s'", customer.customer_id)
        return serialize_customer(customer), 200

    except IntegrityError:
        error_msg = "Cliente com mesmo email ou tx_id já salvo na base :/"
        logger.warning(
            "Error adding customer '%s': %s",
            customer.email,
            error_msg)
        return {"message": error_msg}, 409

    except Exception:
        error_msg = "Não foi possível salvar novo customer :/"
        logger.warning(
            "Error adding customer '%s': %s",
            customer.email,
            error_msg)
        return {"message": error_msg}, 400


@app.get(  # type: ignore[misc]
    "/customers",
    tags=[customer_tag],
    responses={"200": CustomerListSchema, "404": ErrorSchema},
)
# Return all registered customers.
def get_customers():
    """Busca todos os clientes cadastrados na base."""
    logger.debug("Fetching all customers")
    session = Session()
    customers = session.query(Customer).all()

    if not customers:
        return {"customers": []}, 200

    logger.debug("%d customers found", len(customers))
    return serialize_customers(customers), 200


@app.get(  # type: ignore[misc]
    "/customer",
    tags=[customer_tag],
    responses={"200": CustomerViewSchema, "404": ErrorSchema},
)
# Return a specific customer by ID.
def get_customer(query: CustomerSearchSchema):
    """Busca um cliente a partir do seu ID."""
    customer_id = query.customer_id
    logger.debug("Fetching data for customer #%s", customer_id)

    session = Session()
    customer = session.query(Customer).filter(
        Customer.customer_id == customer_id).first()

    if not customer:
        error_msg = "Cliente não encontrado na base :/"
        logger.warning(
            "Error fetching customer '%s': %s",
            customer_id,
            error_msg)
        return {"message": error_msg}, 404

    logger.debug("Customer found: '%s'", customer.customer_id)
    return serialize_customer(customer), 200


@app.delete(  # type: ignore[misc]
    "/customer",
    tags=[customer_tag],
    responses={"200": CustomerDeleteSchema, "404": ErrorSchema},
)
# Delete a customer by ID.
def del_customer(query: CustomerSearchSchema):
    """Remove um cliente a partir do seu ID."""
    customer_id = query.customer_id
    logger.debug("Deleting customer #%s", customer_id)

    session = Session()
    count = session.query(Customer).filter(
        Customer.customer_id == customer_id).delete()
    session.commit()

    if count:
        logger.debug("Customer deleted: #%s", customer_id)
        return {"message": "Cliente removido",
                "customer_id": customer_id}, 200

    error_msg = "Cliente não encontrado na base :/"
    logger.warning("Error deleting customer '%s': %s", customer_id, error_msg)
    return {"message": error_msg}, 404


@app.post(  # type: ignore[misc]
    "/hydrogen-generator",
    tags=[hydrogen_generator_tag],
    responses={
        "200": HydrogenGeneratorViewSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
    },
)
# Create a new hydrogen generator and persist it in the database.
def add_hydrogen_generator(form: HydrogenGeneratorCreateSchema):
    """Adiciona um novo gerador de hidrogênio na base de dados."""
    generator = HydrogenGenerator(
        serial_number=form.serial_number,
        acquisition_type=form.acquisition_type,
        stack_type=form.stack_type,
        number_of_cells=form.number_of_cells,
        stack_voltage=form.stack_voltage,
        current_density=form.current_density,
    )
    logger.debug(
        "Adding generator with serial: '%s'",
        generator.serial_number)

    try:
        session = Session()
        session.add(generator)
        session.commit()
        logger.debug(
            "Generator added with id: '%s'",
            generator.generator_id)
        return format_hydrogen_generator(generator), 200

    except IntegrityError:
        error_msg = "Gerador com mesmo número de série já salvo na base :/"
        logger.warning(
            "Error adding generator '%s': %s",
            generator.serial_number,
            error_msg,
        )
        return {"message": error_msg}, 409

    except Exception:
        error_msg = "Não foi possível salvar novo gerador :/"
        logger.warning(
            "Error adding generator '%s': %s",
            generator.serial_number,
            error_msg,
        )
        return {"message": error_msg}, 400


@app.get(  # type: ignore[misc]
    "/hydrogen-generators",
    tags=[hydrogen_generator_tag],
    responses={"200": HydrogenGeneratorListSchema, "404": ErrorSchema},
)
# Return all registered hydrogen generators.
def get_hydrogen_generators():
    """Busca todos os geradores de hidrogênio cadastrados na base."""
    logger.debug("Fetching all hydrogen generators")

    session = Session()
    generators = session.query(HydrogenGenerator).all()

    if not generators:
        return {"generators": []}, 200

    logger.debug("%d generators found", len(generators))
    return format_hydrogen_generators(generators), 200


@app.get(  # type: ignore[misc]
    "/hydrogen-generator",
    tags=[hydrogen_generator_tag],
    responses={"200": HydrogenGeneratorViewSchema, "404": ErrorSchema},
)
# Return a specific hydrogen generator by serial number.
def get_hydrogen_generator(query: HydrogenGeneratorSearchSchema):
    """Busca um gerador de hidrogênio a partir do seu número de série."""
    serial_number = query.serial_number
    logger.debug(
        "Fetching data for hydrogen generator '%s'",
        serial_number)

    session = Session()
    generator = (
        session.query(HydrogenGenerator)
        .filter(HydrogenGenerator.serial_number == serial_number)
        .first()
    )

    if not generator:
        error_msg = "Gerador de hidrogênio não encontrado na base :/"
        logger.warning(
            "Error fetching hydrogen generator '%s': %s",
            serial_number,
            error_msg)
        return {"message": error_msg}, 404

    logger.debug(
        "Hydrogen generator found: '%s'",
        generator.serial_number)
    return format_hydrogen_generator(generator), 200


@app.delete(  # type: ignore[misc]
    "/hydrogen-generator",
    tags=[hydrogen_generator_tag],
    responses={"200": HydrogenGeneratorDeleteSchema, "404": ErrorSchema},
)
# Delete a hydrogen generator by serial number.
def del_hydrogen_generator(query: HydrogenGeneratorSearchSchema):
    """Remove um gerador de hidrogênio a partir do número de série informado."""
    serial_number = unquote(unquote(query.serial_number))
    logger.debug(
        "Deleting hydrogen generator '%s'",
        serial_number)

    session = Session()
    count = (
        session.query(HydrogenGenerator)
        .filter(HydrogenGenerator.serial_number == serial_number)
        .delete()
    )
    session.commit()

    if count:
        logger.debug("Hydrogen generator deleted: '%s'", serial_number)
        return {"message": "Gerador de hidrogênio removido",
                "serial_number": serial_number}, 200

    error_msg = "Gerador de hidrogênio não encontrado na base :/"
    logger.warning(
        "Error deleting hydrogen generator '%s': %s", serial_number, error_msg
    )
    return {"message": error_msg}, 404


if __name__ == "__main__":
    app.run(debug=True)
