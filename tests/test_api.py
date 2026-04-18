import os
from uuid import uuid4

from alembic.config import Config
from fastapi.testclient import TestClient

from alembic import command

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://inventory_user:inventory_pass@localhost:5432/inventory_dev",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.main import app

alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])
command.upgrade(alembic_cfg, "head")

client = TestClient(app)


def _unique(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def test_create_catalog_conflict_returns_409():
    name = _unique("catalog")
    payload = {"name": name, "description": "primary"}
    first = client.post("/catalogs", json=payload)
    second = client.post("/catalogs", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_patch_missing_catalog_returns_404():
    response = client.patch("/catalogs/99999999", json={"description": "updated"})
    assert response.status_code == 404


def test_create_product_conflict_returns_409():
    sku = _unique("sku")
    payload = {"name": "Keyboard", "sku": sku, "price": "49.99", "quantity": 5}
    first = client.post("/products", json=payload)
    second = client.post("/products", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_assign_and_remove_product_catalog_flow():
    catalog = client.post(
        "/catalogs",
        json={"name": _unique("cat"), "description": "for assign/remove"},
    ).json()
    product = client.post(
        "/products",
        json={"name": "Mouse", "sku": _unique("sku"), "price": "19.99", "quantity": 20},
    ).json()

    assigned = client.patch(
        f"/products/{product['id']}",
        json={"quantity": 25},
    )
    assert assigned.status_code == 200

    bound = client.put(
        f"/products/{product['id']}/catalog",
        json={"catalog_id": catalog["id"]},
    )
    assert bound.status_code == 200
    assert bound.json()["catalog_id"] == catalog["id"]

    unbound = client.delete(f"/products/{product['id']}/catalog")
    assert unbound.status_code == 200
    assert unbound.json()["catalog_id"] is None


def test_products_pagination():
    page = client.get("/products", params={"offset": 0, "limit": 2})
    assert page.status_code == 200
    assert len(page.json()) <= 2
