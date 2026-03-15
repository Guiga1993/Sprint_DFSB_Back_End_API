from flask import redirect
from flask_cors import CORS
from flask_openapi3 import Info, OpenAPI, Tag
from sqlalchemy.exc import IntegrityError

from model import Customer, session_factory
from schemas.customer import (
    CustomerDeleteSchema,
    CustomerListSchema,
    CustomerSchema,
    CustomerSearchSchema,
    CustomerViewSchema,
    apresenta_customer,
    apresenta_customers,
)
from schemas.error import ErrorSchema
from schemas.logger import logger


info = Info(title="H2 Generator API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

home_tag = Tag(name="Documentation", description="OpenAPI documentation selector")
customer_tag = Tag(name="Customer", description="Customer CRUD operations")


@app.get('/', tags=[home_tag])
def home():
    """Redirect to OpenAPI documentation."""
    return redirect('/openapi')


@app.post('/customer', tags=[customer_tag],
          responses={"200": CustomerViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_customer(form: CustomerSchema):
    """Add a new customer."""
    customer = Customer(name=form.name, email=form.email, tx_id=form.tx_id)
    logger.debug(f"Adding customer: '{customer.name}'")
    session = None

    try:
        session = session_factory()
        session.add(customer)
        session.commit()
        session.refresh(customer)
        return apresenta_customer(customer), 200

    except IntegrityError:
        error_msg = "Customer with same email or tx_id already exists."
        logger.warning(f"Error adding customer '{customer.name}': {error_msg}")
        return {"message": error_msg}, 409

    except Exception:
        error_msg = "Unable to add customer."
        logger.warning(f"Error adding customer '{customer.name}': {error_msg}")
        return {"message": error_msg}, 400

    finally:
        if session is not None:
            session.close()


@app.get('/customers', tags=[customer_tag],
         responses={"200": CustomerListSchema, "404": ErrorSchema})
def get_customers():
    """Get all customers."""
    logger.debug("Fetching all customers")
    session = session_factory()

    try:
        customers = session.query(Customer).all()
        return apresenta_customers(customers), 200
    finally:
        session.close()


@app.get('/customer', tags=[customer_tag],
         responses={"200": CustomerViewSchema, "404": ErrorSchema})
def get_customer(query: CustomerSearchSchema):
    """Get customer by ID."""
    customer_id = query.customer_id
    logger.debug(f"Fetching customer #{customer_id}")
    session = session_factory()

    try:
        customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()

        if not customer:
            error_msg = "Customer not found."
            logger.warning(f"Error fetching customer '{customer_id}': {error_msg}")
            return {"message": error_msg}, 404

        return apresenta_customer(customer), 200
    finally:
        session.close()


@app.put('/customer', tags=[customer_tag],
         responses={"200": CustomerViewSchema, "404": ErrorSchema, "409": ErrorSchema, "400": ErrorSchema})
def update_customer(query: CustomerSearchSchema, form: CustomerSchema):
    """Update customer by ID."""
    customer_id = query.customer_id
    logger.debug(f"Updating customer #{customer_id}")
    session = session_factory()

    try:
        customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()

        if not customer:
            error_msg = "Customer not found."
            logger.warning(f"Error updating customer '{customer_id}': {error_msg}")
            return {"message": error_msg}, 404

        customer.name = form.name
        customer.email = form.email
        customer.tx_id = form.tx_id
        session.commit()
        session.refresh(customer)

        return apresenta_customer(customer), 200

    except IntegrityError:
        session.rollback()
        error_msg = "Email or tx_id already in use by another customer."
        logger.warning(f"Error updating customer '{customer_id}': {error_msg}")
        return {"message": error_msg}, 409

    except Exception:
        session.rollback()
        error_msg = "Unable to update customer."
        logger.warning(f"Error updating customer '{customer_id}': {error_msg}")
        return {"message": error_msg}, 400

    finally:
        session.close()


@app.delete('/customer', tags=[customer_tag],
            responses={"200": CustomerDeleteSchema, "404": ErrorSchema})
def delete_customer(query: CustomerSearchSchema):
    """Delete customer by ID."""
    customer_id = query.customer_id
    logger.debug(f"Deleting customer #{customer_id}")
    session = session_factory()

    try:
        count = session.query(Customer).filter(Customer.customer_id == customer_id).delete()
        session.commit()

        if count:
            return {"message": "Customer removed", "customer_id": customer_id}, 200

        error_msg = "Customer not found."
        logger.warning(f"Error deleting customer '{customer_id}': {error_msg}")
        return {"message": error_msg}, 404

    finally:
        session.close()
