# Shop Inventory Management API

FastAPI service for managing catalogs and products, including product-catalog assignment.

## Run locally

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Open Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
Alternative ReDoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

## Run with Docker (single command)

- Development (hot reload):
  `docker compose -f docker-compose.dev.yml up --build`
- Production:
  `docker compose --env-file .env.prod up --build -d`

Swagger UI: [http://127.0.0.1/docs](http://127.0.0.1/docs)
ReDoc: [http://127.0.0.1/redoc](http://127.0.0.1/redoc)

### Production deployment setup

1. Create env file:
   `cp .env.prod.example .env.prod`
2. Update `.env.prod` values (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `CADDY_DOMAIN`, `CADDY_EMAIL`).
3. Start all services:
   `docker compose --env-file .env.prod up --build -d`

Notes:

- Production compose now fails fast when required Postgres env vars are missing.
- API runs with multiple workers (`UVICORN_WORKERS`, default `3`).

Production stack includes:

- `db` (PostgreSQL)
- `migrate` (Alembic migrations)
- `api` (FastAPI app)
- `caddy` (reverse proxy and TLS terminator)

### Dev Docker utilities

The development compose stack now includes Docker-only utility services:

- `db` (PostgreSQL) on `localhost:5432`
- `migrate` (runs `alembic upgrade head` before API startup)
- `pgadmin` on [http://localhost:5050](http://localhost:5050)
- `test` (runs `pytest -q`, tools profile)
- `lint` (runs `ruff check .`, tools profile)

Run utility profile services:

```bash
docker compose -f docker-compose.dev.yml --profile tools up --build
```

## API capabilities

- Catalog CRUD (`/catalogs`)
- Product CRUD (`/products`)
- Assign product to catalog (`PUT /products/{product_id}/catalog`)
- Remove product from catalog (`DELETE /products/{product_id}/catalog`)
- List products by catalog (`GET /catalogs/{catalog_id}/products`)
- Partial updates via `PATCH /catalogs/{catalog_id}` and `PATCH /products/{product_id}`
- Pagination on list endpoints with `offset` and `limit` query params

## Using the API via Swagger

1. Open `/docs`.
2. Create a catalog using `POST /catalogs`.
3. Create a product using `POST /products`.
4. Assign it to the catalog with `PUT /products/{product_id}/catalog`.
5. Retrieve catalog products with `GET /catalogs/{catalog_id}/products`.

## Project structure

- `app/core`: database and session management
- `app/models`: SQLAlchemy ORM models
- `app/schemas`: Pydantic request/response models
- `app/services`: business logic layer
- `app/routers`: API route definitions
- `app/main.py`: FastAPI app initialization
- `main.py`: ASGI app entrypoint
- `docker-compose.dev.yml`: development container setup
- `docker-compose.yml`: production container setup
- `alembic`: database migrations

## Testing

```bash
docker compose -f docker-compose.dev.yml run --rm -e TEST_DATABASE_URL=postgresql+psycopg://inventory_user:inventory_pass@db:5432/inventory_dev test
```

## Linting (Ruff)

```bash
docker compose -f docker-compose.dev.yml run --rm lint
```
# shop-inventory-management
