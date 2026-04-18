from fastapi import FastAPI

from app.routers.catalogs import router as catalogs_router
from app.routers.products import router as products_router

app = FastAPI(
    title="Shop Inventory Management API",
    summary="API for catalog and product inventory operations.",
    description=(
        "A REST API for managing shop catalogs and products.\n\n"
        "## Main Features\n"
        "- Catalog CRUD operations\n"
        "- Product CRUD operations\n"
        "- Assign or remove products from catalogs\n"
        "- Pagination on list endpoints\n\n"
        "## Quick Start in Swagger\n"
        "1. Create a catalog (`POST /catalogs`)\n"
        "2. Create a product (`POST /products`)\n"
        "3. Assign product to a catalog (`PUT /products/{product_id}/catalog`)\n"
        "4. Query catalog products (`GET /catalogs/{catalog_id}/products`)\n"
    ),
    version="1.0.0",
    contact={"name": "Inventory API Support", "email": "support@example.com"},
    license_info={"name": "MIT"},
    openapi_tags=[
        {
            "name": "Catalogs",
            "description": "Catalog lifecycle and catalog-scoped product listing.",
        },
        {
            "name": "Products",
            "description": "Product lifecycle and catalog assignment controls.",
        },
        {"name": "Health", "description": "Service health and readiness probes."},
    ],
)

app.include_router(catalogs_router)
app.include_router(products_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Basic health endpoint for uptime checks."""
    return {"status": "ok"}
