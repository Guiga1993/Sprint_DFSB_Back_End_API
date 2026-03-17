# =============================================================================
# Hydrogen Generator API — Main Application
# =============================================================================
# Flask + OpenAPI application that exposes CRUD endpoints for managing
# customers, hydrogen generators, and the asset links between them.
# =============================================================================


# ── Standard library imports ─────────────────────────────────────────────────
import re
from urllib.parse import unquote

# ── Third-party imports ──────────────────────────────────────────────────────
from flask import redirect
from flask_cors import CORS
from flask_openapi3 import OpenAPI, Info, Tag  # type: ignore[attr-defined]
from sqlalchemy.exc import IntegrityError

# ── Local imports — ORM models ───────────────────────────────────────────────
from model import Customer, CustomerGeneratorAsset, HydrogenGenerator, session_factory

# ── Local imports — Customer schemas & serializers ───────────────────────────
from schemas.customer import (
    CustomerDeleteSchema,
    CustomerListSchema,
    CustomerSchema,
    CustomerSearchSchema,
    CustomerViewSchema,
    get_customer as serialize_customer,
    get_customers as serialize_customers,
)

# ── Local imports — Error schema ─────────────────────────────────────────────
from schemas.error import ErrorSchema

# ── Local imports — Hydrogen Generator schemas & serializers ─────────────────
from schemas.hydrogen_generator import (
    HydrogenGeneratorCreateSchema,
    HydrogenGeneratorDeleteSchema,
    HydrogenGeneratorListSchema,
    HydrogenGeneratorSearchSchema,
    HydrogenGeneratorViewSchema,
    get_hydrogen_generator as serialize_generator,
    get_hydrogen_generators as serialize_generators,
)

# ── Local imports — Customer-Generator Asset schemas & serializers ───────────
from schemas.customer_generator_asset import (
    CustomerGeneratorAssetDeleteSchema,
    CustomerGeneratorAssetListSchema,
    CustomerGeneratorAssetSchema,
    CustomerGeneratorAssetSearchSchema,
    CustomerGeneratorAssetViewSchema,
    get_asset as serialize_asset,
    get_assets as serialize_assets,
)

# ── Local imports — Logger ───────────────────────────────────────────────────
from schemas.logger import logger


# =============================================================================
# Application Setup
# =============================================================================

# SQLAlchemy scoped-session factory used by all route handlers.
Session = session_factory

# OpenAPI metadata displayed in the Swagger UI header.
info = Info(title="Hydrogen Generator API", version="1.0.0")
app = OpenAPI(__name__, info=info)

# Preserve field insertion order in JSON responses.
app.json.sort_keys = False  # type: ignore[assignment]

# Allow cross-origin requests so the frontend can reach the API.
CORS(app)


# =============================================================================
# Swagger UI Tags
# =============================================================================
# Tags group related endpoints in the interactive documentation page.

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

asset_tag = Tag(
    name="Vínculo Cliente-Gerador",
    description="Adição, visualização e remoção de vínculos entre clientes e geradores",
)


# =============================================================================
# Home / Documentation Redirect
# =============================================================================


# Redirect the root path to the interactive OpenAPI documentation page.
@app.get("/", tags=[home_tag])  # type: ignore
def home():
    """Redirects to /openapi, offering multiple API documentation views."""
    return redirect("/openapi")


# =============================================================================
# Customer Endpoints
# =============================================================================
# POST   /customer   — Create a new customer
# GET    /customers  — List all customers
# GET    /customer   — Retrieve a single customer by ID
# DELETE /customer   — Delete a customer by ID (cascades to asset links)
# =============================================================================


# ── POST /customer ───────────────────────────────────────────────────────────
# Create a new customer after validating that name, email, and tax ID are
# unique. Returns 409 if any duplicate is found, 400 on unexpected errors.
@app.post(  # type: ignore[misc]
    "/customer",
    tags=[customer_tag],
    responses={
        "200": CustomerViewSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
    },
)
def add_customer(form: CustomerSchema):
    """Add a new customer to the database."""
    # Step 1: Build the ORM object from validated payload.
    customer = Customer(name=form.name, email=form.email, tx_id=form.tx_id)
    logger.debug("Adding customer with email: '%s'", customer.email)

    session = Session()
    try:
        # Step 2: Validate uniqueness one field at a time for clearer feedback.
        if session.query(Customer).filter(Customer.name == form.name).first():
            error_msg = "A customer with the same name already exists in the database."
            logger.warning("Duplicate name '%s': %s", form.name, error_msg)
            return {"message": error_msg}, 409

        if session.query(Customer).filter(Customer.email == form.email).first():
            error_msg = "A customer with the same email already exists in the database."
            logger.warning("Duplicate email '%s': %s", form.email, error_msg)
            return {"message": error_msg}, 409

        if session.query(Customer).filter(Customer.tx_id == form.tx_id).first():
            error_msg = "A customer with the same Tax ID already exists in the database."
            logger.warning("Duplicate tx_id '%s': %s", form.tx_id, error_msg)
            return {"message": error_msg}, 409

        # Step 3: Persist and return the created entity.
        session.add(customer)
        session.commit()
        logger.debug("Customer added with id: '%s'", customer.customer_id)
        return serialize_customer(customer), 200

    except IntegrityError:
        # Safety net for race conditions between duplicate checks and insert.
        error_msg = "Data conflict while saving the customer."
        logger.warning(
            "Error adding customer '%s': %s", customer.email, error_msg)
        return {"message": error_msg}, 409

    except Exception:
        # Catch-all for unexpected database or serialization errors.
        error_msg = "Unable to save the new customer."
        logger.warning(
            "Error adding customer '%s': %s", customer.email, error_msg)
        return {"message": error_msg}, 400

    finally:
        session.close()


# ── GET /customers ───────────────────────────────────────────────────────────
# Return all registered customers. Returns an empty list when none exist.
@app.get(  # type: ignore[misc]
    "/customers",
    tags=[customer_tag],
    responses={"200": CustomerListSchema, "404": ErrorSchema},
)
def get_customers():  # type: ignore
    """Retrieve all registered customers."""
    logger.debug("Fetching all customers")
    session = Session()
    try:
        customers = session.query(Customer).all()

        # Return an explicit empty list instead of 404 for collection endpoints.
        if not customers:
            return {"customers": []}, 200  # type: ignore

        logger.debug("%d customers found", len(customers))
        return serialize_customers(customers), 200
    finally:
        session.close()


# ── GET /customer ────────────────────────────────────────────────────────────
# Return a single customer by primary key. Returns 404 if not found.
@app.get(  # type: ignore[misc]
    "/customer",
    tags=[customer_tag],
    responses={"200": CustomerViewSchema, "404": ErrorSchema},
)
def get_customer(query: CustomerSearchSchema):
    """Retrieve a single customer by ID."""
    customer_id = query.customer_id
    logger.debug("Fetching data for customer #%s", customer_id)

    session = Session()
    try:
        customer = session.query(Customer).filter(
            Customer.customer_id == customer_id).first()

        if not customer:
            error_msg = "Cliente não encontrado no banco de dados."
            logger.warning(
                "Error fetching customer '%s': %s", customer_id, error_msg)
            return {"message": error_msg}, 404

        logger.debug("Customer found: '%s'", customer.customer_id)
        return serialize_customer(customer), 200
    finally:
        session.close()


# ── DELETE /customer ─────────────────────────────────────────────────────────
# Delete a customer by primary key. Also removes any asset links that
# reference this customer. Returns 404 if the ID does not exist.
@app.delete(  # type: ignore[misc]
    "/customer",
    tags=[customer_tag],
    responses={"200": CustomerDeleteSchema, "404": ErrorSchema},
)
def del_customer(query: CustomerSearchSchema):  # type: ignore
    """Delete a customer by ID."""
    customer_id = query.customer_id
    logger.debug("Deleting customer #%s", customer_id)

    session = Session()
    try:
        count = session.query(Customer).filter(
            Customer.customer_id == customer_id).delete()

        if count:
            # Cascade: remove all asset links referencing this customer.
            session.query(CustomerGeneratorAsset).filter(
                CustomerGeneratorAsset.customer_id == customer_id).delete()
            session.commit()
            logger.debug("Customer deleted: #%s", customer_id)
            return {"message": "Customer deleted",
                    "customer_id": customer_id}, 200  # type: ignore

        session.commit()
        error_msg = "Cliente não encontrado no banco de dados."
        logger.warning("Error deleting customer '%s': %s", customer_id, error_msg)
        return {"message": error_msg}, 404
    finally:
        session.close()


# =============================================================================
# Hydrogen Generator Endpoints
# =============================================================================
# POST   /hydrogen-generator   — Create a new generator
# GET    /hydrogen-generators  — List all generators
# GET    /hydrogen-generator   — Retrieve a single generator by serial number
# DELETE /hydrogen-generator   — Delete a generator by serial number
#                                (cascades to asset links)
# =============================================================================


# ── POST /hydrogen-generator ─────────────────────────────────────────────────
# Create a new hydrogen generator. Serial number uniqueness is enforced by the
# database constraint. Returns 409 on duplicate serial numbers.
@app.post(  # type: ignore[misc]
    "/hydrogen-generator",
    tags=[hydrogen_generator_tag],
    responses={
        "200": HydrogenGeneratorViewSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
    },
)
def add_hydrogen_generator(form: HydrogenGeneratorCreateSchema):
    """Add a new hydrogen generator to the database."""
    # Step 1: Build the ORM object from validated payload.
    generator = HydrogenGenerator(
        serial_number=form.serial_number,
        acquisition_type=form.acquisition_type,
        stack_type=form.stack_type,
        number_of_cells=form.number_of_cells,
        stack_voltage=form.stack_voltage,
        current_density=form.current_density,
    )
    logger.debug(
        "Adding generator with serial: '%s'", generator.serial_number)

    session = Session()
    try:
        # Step 2: Persist directly; serial uniqueness is enforced by DB constraint.
        session.add(generator)
        session.commit()
        logger.debug(
            "Generator added with id: '%s'", generator.generator_id)
        return serialize_generator(generator), 200

    except IntegrityError:
        # Duplicate serial_number detected by the DB unique constraint.
        error_msg = "A hydrogen generator with the same serial number already exists in the database."
        logger.warning(
            "Error adding generator '%s': %s",
            generator.serial_number, error_msg)
        return {"message": error_msg}, 409

    except Exception:
        # Catch-all for unexpected database or serialization errors.
        error_msg = "Unable to save the new hydrogen generator."
        logger.warning(
            "Error adding generator '%s': %s",
            generator.serial_number, error_msg)
        return {"message": error_msg}, 400

    finally:
        session.close()


# ── GET /hydrogen-generators ─────────────────────────────────────────────────
# Return all registered hydrogen generators. Returns an empty list when
# none exist.
@app.get(  # type: ignore[misc]
    "/hydrogen-generators",
    tags=[hydrogen_generator_tag],
    responses={"200": HydrogenGeneratorListSchema, "404": ErrorSchema},
)
def get_hydrogen_generators():  # type: ignore
    """Retrieve all registered hydrogen generators."""
    logger.debug("Fetching all hydrogen generators")
    session = Session()
    try:
        generators = session.query(HydrogenGenerator).all()

        # Return an explicit empty list instead of 404 for collection endpoints.
        if not generators:
            return {"generators": []}, 200  # type: ignore

        logger.debug("%d generators found", len(generators))
        return serialize_generators(generators), 200
    finally:
        session.close()


# ── GET /hydrogen-generator ──────────────────────────────────────────────────
# Return a single hydrogen generator by serial number. Returns 404 if not
# found.
@app.get(  # type: ignore[misc]
    "/hydrogen-generator",
    tags=[hydrogen_generator_tag],
    responses={"200": HydrogenGeneratorViewSchema, "404": ErrorSchema},
)
def get_hydrogen_generator(query: HydrogenGeneratorSearchSchema):
    """Retrieve a single hydrogen generator by serial number."""
    serial_number = query.serial_number
    logger.debug("Fetching data for hydrogen generator '%s'", serial_number)

    session = Session()
    try:
        generator = (
            session.query(HydrogenGenerator)
            .filter(HydrogenGenerator.serial_number == serial_number)
            .first()
        )

        if not generator:
            error_msg = "Hydrogen generator not found in the database."
            logger.warning(
                "Error fetching hydrogen generator '%s': %s",
                serial_number, error_msg)
            return {"message": error_msg}, 404

        logger.debug("Hydrogen generator found: '%s'", generator.serial_number)
        return serialize_generator(generator), 200
    finally:
        session.close()


# ── DELETE /hydrogen-generator ───────────────────────────────────────────────
# Delete a hydrogen generator by serial number. The serial_number is
# double-unquoted to handle URL-encoded values. Also removes any asset links
# that reference this generator. Returns 404 if the serial number is not found.
@app.delete(  # type: ignore[misc]
    "/hydrogen-generator",
    tags=[hydrogen_generator_tag],
    responses={"200": HydrogenGeneratorDeleteSchema, "404": ErrorSchema, "400": ErrorSchema},
)
def del_hydrogen_generator(query: HydrogenGeneratorSearchSchema):
    """Delete a hydrogen generator by serial number."""
    # Normalize encoded serial values sent in query strings.
    serial_number = unquote(unquote(query.serial_number))
    logger.debug("Deleting hydrogen generator '%s'", serial_number)

    # Deletion is intentionally restricted to the current serial format only.
    if not re.fullmatch(r"GEN-\d{4}", serial_number):
        error_msg = "serial_number must follow the format GEN-0000 for deletion."
        logger.warning("Invalid serial format for delete '%s': %s", serial_number, error_msg)
        return {"message": error_msg}, 400

    session = Session()
    try:
        # Look up the generator to obtain its PK before deleting.
        generator = (
            session.query(HydrogenGenerator)
            .filter(HydrogenGenerator.serial_number == serial_number)
            .first()
        )

        if generator:
            generator_id = generator.generator_id
            # Delete main record first, then cleanup relationship rows.
            session.delete(generator)
            # Cascade: remove all asset links referencing this generator.
            session.query(CustomerGeneratorAsset).filter(
                CustomerGeneratorAsset.generator_id == generator_id).delete()
            session.commit()
            logger.debug("Hydrogen generator deleted: '%s'", serial_number)
            return {"message": "Hydrogen generator deleted",
                    "serial_number": serial_number}, 200

        error_msg = "Hydrogen generator not found in the database."
        logger.warning(
            "Error deleting hydrogen generator '%s': %s", serial_number, error_msg)
        return {"message": error_msg}, 404
    finally:
        session.close()


# =============================================================================
# Customer-Generator Asset Endpoints
# =============================================================================
# POST   /asset   — Create a new customer-generator link
# GET    /assets  — List all asset links
# GET    /asset   — Retrieve a single asset link by ID
# DELETE /asset   — Delete an asset link by ID
# =============================================================================


# ── POST /asset ──────────────────────────────────────────────────────────────
# Create a new link between a customer and a hydrogen generator. Both the
# customer and generator must already exist. Returns 404 if either foreign
# key is invalid, 409 on integrity conflicts.
@app.post(  # type: ignore[misc]
    "/asset",
    tags=[asset_tag],
    responses={
        "200": CustomerGeneratorAssetViewSchema,
        "404": ErrorSchema,
        "409": ErrorSchema,
        "400": ErrorSchema,
    },
)
def add_asset(form: CustomerGeneratorAssetSchema):
    """Add a new customer-generator asset link to the database."""
    # Step 1: Build ORM object from validated payload.
    asset = CustomerGeneratorAsset(
        customer_id=form.customer_id,
        generator_id=form.generator_id,
        generator_qtd=form.generator_qtd,
        installation_date=form.installation_date,
    )
    logger.debug(
        "Adding asset link: customer=%s, generator=%s",
        asset.customer_id, asset.generator_id)

    session = Session()
    try:
        # Step 2a: Validate foreign-key references before insertion.
        if not session.query(Customer).filter(
                Customer.customer_id == form.customer_id).first():
            error_msg = "Cliente não encontrado no banco de dados."
            logger.warning(
                "Cliente #%s não encontrado ao criar ativo", form.customer_id)
            return {"message": error_msg}, 404

        # Step 2b: Validate generator reference.
        if not session.query(HydrogenGenerator).filter(
                HydrogenGenerator.generator_id == form.generator_id).first():
            error_msg = "Gerador não encontrado no banco de dados."
            logger.warning(
                "Gerador #%s não encontrado ao criar ativo", form.generator_id)
            return {"message": error_msg}, 404

        # Step 3: Persist and return created link.
        session.add(asset)
        session.commit()
        logger.debug("Asset added with id: '%s'", asset.asset_id)
        return serialize_asset(asset), 200

    except IntegrityError:
        # Data conflict detected by a database constraint.
        error_msg = "Data conflict when saving the asset."
        logger.warning(
            "Error adding asset (customer=%s, generator=%s): %s",
            form.customer_id, form.generator_id, error_msg)
        return {"message": error_msg}, 409

    except Exception as e:
        # Catch-all for unexpected database or serialization errors.
        error_msg = "Unable to save the new asset."
        logger.warning(
            "Error adding asset (customer=%s, generator=%s): %s — %s",
            form.customer_id, form.generator_id, error_msg, e)
        return {"message": error_msg}, 400

    finally:
        session.close()


# ── GET /assets ──────────────────────────────────────────────────────────────
# Return all registered customer-generator asset links. Returns an empty
# list when none exist.
@app.get(  # type: ignore[misc]
    "/assets",
    tags=[asset_tag],
    responses={"200": CustomerGeneratorAssetListSchema, "404": ErrorSchema},
)
def get_assets():  # type: ignore
    """Retrieve all customer-generator asset links."""
    logger.debug("Fetching all asset links")
    session = Session()
    try:
        assets = session.query(CustomerGeneratorAsset).all()

        # Return an explicit empty list instead of 404 for collection endpoints.
        if not assets:
            return {"assets": []}, 200  # type: ignore

        logger.debug("%d asset links found", len(assets))
        return serialize_assets(assets), 200
    finally:
        session.close()


# ── GET /asset ───────────────────────────────────────────────────────────────
# Return a single asset link by primary key. Returns 404 if not found.
@app.get(  # type: ignore[misc]
    "/asset",
    tags=[asset_tag],
    responses={"200": CustomerGeneratorAssetViewSchema, "404": ErrorSchema},
)
def get_asset(query: CustomerGeneratorAssetSearchSchema):
    """Retrieve a single customer-generator asset link by ID."""
    asset_id = query.asset_id
    logger.debug("Fetching data for asset #%s", asset_id)

    session = Session()
    try:
        asset = session.query(CustomerGeneratorAsset).filter(
            CustomerGeneratorAsset.asset_id == asset_id).first()

        if not asset:
            error_msg = "Asset not found in the database."
            logger.warning(
                "Error fetching asset '%s': %s", asset_id, error_msg)
            return {"message": error_msg}, 404

        logger.debug("Asset found: '%s'", asset.asset_id)
        return serialize_asset(asset), 200
    finally:
        session.close()


# ── DELETE /asset ────────────────────────────────────────────────────────────
# Delete an asset link by primary key. Returns 404 if the ID does not exist.
@app.delete(  # type: ignore[misc]
    "/asset",
    tags=[asset_tag],
    responses={
        "200": CustomerGeneratorAssetDeleteSchema,
        "404": ErrorSchema,
        "400": ErrorSchema,
    },
)

def del_asset(query: CustomerGeneratorAssetSearchSchema):  # type: ignore
    """Delete a customer-generator asset link by ID."""
    asset_id = query.asset_id
    logger.debug("Deleting asset #%s", asset_id)

    session = Session()
    try:
        count = session.query(CustomerGeneratorAsset).filter(
            CustomerGeneratorAsset.asset_id == asset_id).delete()
        session.commit()

        # DELETE returns success only when a row was actually removed.
        if count:
            logger.debug("Asset deleted: #%s", asset_id)
            return {"message": "Asset deleted",
                    "asset_id": asset_id}, 200  # type: ignore

        error_msg = "Asset not found in the database."
        logger.warning("Error deleting asset '%s': %s", asset_id, error_msg)
        return {"message": error_msg}, 404

    except Exception:
        # Catch-all for unexpected database errors during deletion.
        error_msg = "Error deleting asset."
        logger.warning("Error deleting asset '%s': %s", asset_id, error_msg)
        return {"message": error_msg}, 400

    finally:
        session.close()


# =============================================================================
# Application Entry Point
# =============================================================================
# Starts the Flask development server only when this file is executed directly
# (i.e. `python app.py`). Ignored when imported as a module.
# debug=True enables auto-reload on code changes and verbose error pages.

if __name__ == "__main__":
    app.run(debug=True)
