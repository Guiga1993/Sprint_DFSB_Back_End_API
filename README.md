## Backend–Frontend Route Mapping

Below is a mapping of each backend API route to its usage in the frontend UI:

### Customers

|                                        |                                    		           |
|            Route Usage                 |						Frontend					   |
|----------------------------------------|-----------------------------------------------------|
| POST   /customer                       | “Cadastrar Cliente” button (customer form)          |
| GET    /customers                      | “Listar Todos” button (customer section)            |
| GET    /customer?customer_id=...       | “Buscar” button (search by ID in customer section)  |
| DELETE /customer?customer_id=...       | Delete (X) button in customer table                 |

### Hydrogen Generators

| Route                                         | Frontend Usage                                         |
|-----------------------------------------------|--------------------------------------------------------|
| POST   /hydrogen-generator                    | “Cadastrar Gerador” button (generator form)            |
| GET    /hydrogen-generators                   | “Listar Todos” button (generator section)              |
| GET    /hydrogen-generator?serial_number=...  | “Buscar” button (search by serial in generator section)|
| DELETE /hydrogen-generator?serial_number=...  | Delete (X) button in generator table                   |

### Customer-Generator Links (Assets)

| Route                                  | Frontend Usage                                      |
|----------------------------------------|-----------------------------------------------------|
| POST   /asset                          | “Vincular” button (asset form)                      |
| GET    /assets                         | “Listar Todos” button (asset section)               |
| GET    /asset?asset_id=...             | “Buscar” button (search by ID in asset section)     |
| DELETE /asset?asset_id=...             | Delete (X) button in asset table                    |

All backend routes are directly accessible from the frontend UI.
# Hydrogen Generator API (Backend)

Backend REST API for managing:
- Customers
- Hydrogen generators
- Customer-generator links (assets)

The project is built with Flask, OpenAPI (flask-openapi3), SQLAlchemy, and SQLite.

## Project Overview

This API provides CRUD operations for the MVP domain and exposes interactive OpenAPI documentation.

Main features:
- Create, list, search, and delete customers
- Create, list, search, and delete hydrogen generators
- Create, list, search, and delete customer-generator links
- Input validation via Pydantic schemas
- Structured logging to console and rotating file logs

## Tech Stack

- Python
- Flask
- flask-openapi3 (Swagger/ReDoc/RapiDoc)
- SQLAlchemy + SQLAlchemy-Utils
- SQLite (local file database)

## Prerequisites

Before running the project, install:

1. **Python 3.10+** (recommended 3.11 or newer)
2. **update pip** (usually included with Python)
3. (Optional but recommended) **venv** for isolated dependencies

To verify Python installation:

```bash
python --version
```

## Installation

From the backend folder (`Sprint_DFSB_Back_End_API`):

1. Create virtual environment:

```bash
python -m venv .venv
```

2. Activate virtual environment:

- **Windows (PowerShell)**

```powershell
& ".\.venv\Scripts\Activate.ps1"
```

- **Linux / macOS**

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Basic Configuration

No external `.env` configuration is required for the default setup.

On startup, the system automatically:
- Creates the `database/` folder (if missing)
- Creates `database/db.sqlite3` (if missing)
- Creates database tables from SQLAlchemy models
- Creates log directory `logs/h2_system/` and log file `activity.log`

## Running the API

Start the application:

```bash
python app.py
```

Default address:
- `http://127.0.0.1:5000`


## API Documentation

After starting the server, open in your browser:

- Swagger UI: `http://127.0.0.1:5000/openapi`

The root path `/` redirects to the OpenAPI docs.

## Frontend Usage Notes

- The frontend tables (customers, generators, assets) are empty by default when the page loads.
- Data is only shown after the user clicks the **Listar Todos** (List All) button or performs a search (e.g., by ID or serial number).
- After adding a new record, the table is not updated automatically; use **Listar Todos** or search to view the new entry.
- Each section also has a **Limpar Tabela** (Clear Table) button, which clears the table in the HTML only (no data is deleted from the database).


## Route Reference

All endpoints are available under the same base URL:

- `http://127.0.0.1:5000`

### 1) Home / Docs

#### `GET /`
- **Description:** Redirects to the OpenAPI page.
- **Request:** No body, no query params.
- **Response:** HTTP redirect to `/openapi`.
- **Status codes:**
	- `302` Redirect

### 2) Customers

#### `POST /customer`
- **Description:** Creates a new customer.
- **Request (form-data):**
	- `name` (string)
	- `email` (string, valid email)
	- `tx_id` (string, format `000-00-0000`)
- **Success response (`200`):**
	- `customer_id` (int)
	- `name` (string)
	- `email` (string)
	- `tx_id` (string)
- **Status codes:**
	- `200` Created/saved successfully
	- `409` Duplicate data conflict
	- `400` Unexpected save error

#### `GET /customers`
- **Description:** Returns all customers.
- **Request:** No body, no query params.
- **Success response (`200`):**
	- `{ "customers": [ ... ] }` where each item is:
		- `customer_id`, `name`, `email`, `tx_id`
- **Status codes:**
	- `200` Always returns list (can be empty)

#### `GET /customer?customer_id=<id>`
- **Description:** Returns one customer by ID.
- **Request (query):**
	- `customer_id` (int > 0)
- **Success response (`200`):**
	- `customer_id`, `name`, `email`, `tx_id`
- **Status codes:**
	- `200` Found
	- `404` Not found

#### `DELETE /customer?customer_id=<id>`
- **Description:** Deletes a customer by ID (and related asset links).
- **Request (query):**
	- `customer_id` (int > 0)
- **Success response (`200`):**
	- `message` (string)
	- `customer_id` (int)
- **Status codes:**
	- `200` Deleted
	- `404` Not found

### 3) Hydrogen Generators

#### `POST /hydrogen-generator`
- **Description:** Creates a new hydrogen generator.
- **Request (form-data):**
	- `serial_number` (string, format `GEN-0000`)
	- `acquisition_type` (string: `Leasing | Renting | Direct Sales`)
	- `stack_type` (string: `PEMFC | Alcaline | SOFC | AEMFC | Other/Personalized`)
	- `number_of_cells` (int, 1..5000)
	- `stack_voltage` (float, >0 and <=2000)
	- `current_density` (float, >0 and <=5000)
- **Success response (`200`):**
	- `generator_id`, `serial_number`, `acquisition_type`, `stack_type`,
		`number_of_cells`, `stack_voltage`, `current_density`
- **Status codes:**
	- `200` Created/saved successfully
	- `409` Duplicate serial number
	- `400` Unexpected save error

#### `GET /hydrogen-generators`
- **Description:** Returns all hydrogen generators.
- **Request:** No body, no query params.
- **Success response (`200`):**
	- `{ "generators": [ ... ] }` where each item contains generator fields
- **Status codes:**
	- `200` Always returns list (can be empty)

#### `GET /hydrogen-generator?serial_number=<serial>`
- **Description:** Returns one generator by serial number.
- **Request (query):**
	- `serial_number` (string; supported for lookup)
- **Success response (`200`):**
	- `generator_id`, `serial_number`, `acquisition_type`, `stack_type`,
		`number_of_cells`, `stack_voltage`, `current_density`
- **Status codes:**
	- `200` Found
	- `404` Not found
	- `422` Query validation error

#### `DELETE /hydrogen-generator?serial_number=<serial>`
- **Description:** Deletes one generator by serial number.
- **Request (query):**
	- `serial_number` (string, **must match `GEN-0000`** for deletion)
- **Success response (`200`):**
	- `message` (string)
	- `serial_number` (string)
- **Status codes:**
	- `200` Deleted
	- `400` Invalid serial format for deletion
	- `404` Not found
	- `422` Query validation error

### 4) Customer-Generator Links (Assets)

#### `POST /asset`
- **Description:** Creates a link between a customer and a generator.
- **Request (form-data):**
	- `customer_id` (int > 0)
	- `generator_id` (int > 0)
	- `generator_qtd` (int, 1..10000)
	- `installation_date` (optional datetime)
- **Success response (`200`):**
	- `asset_id`, `customer_id`, `generator_id`, `generator_qtd`, `installation_date`
- **Status codes:**
	- `200` Created/saved successfully
	- `404` Referenced customer or generator not found
	- `409` Data conflict
	- `400` Unexpected save error

#### `GET /assets`
- **Description:** Returns all asset links.
- **Request:** No body, no query params.
- **Success response (`200`):**
	- `{ "assets": [ ... ] }` where each item contains asset fields
- **Status codes:**
	- `200` Always returns list (can be empty)

#### `GET /asset?asset_id=<id>`
- **Description:** Returns one asset link by ID.
- **Request (query):**
	- `asset_id` (int > 0)
- **Success response (`200`):**
	- `asset_id`, `customer_id`, `generator_id`, `generator_qtd`, `installation_date`
- **Status codes:**
	- `200` Found
	- `404` Not found

#### `DELETE /asset?asset_id=<id>`
- **Description:** Deletes one asset link by ID.
- **Request (query):**
	- `asset_id` (int > 0)
- **Success response (`200`):**
	- `message` (string)
	- `asset_id` (int)
- **Status codes:**
	- `200` Deleted
	- `404` Not found
	- `400` Unexpected delete error

## Notes

- The frontend project should call this API at `http://127.0.0.1:5000`.
- Tables are not auto-populated; user action is required to display data.
- The **Limpar Tabela** button only clears the table view, not the database.
- Some validations are intentionally strict (for example, generator serial format).
- Logs are written to `logs/h2_system/activity.log`.
