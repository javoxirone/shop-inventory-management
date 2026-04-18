from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.catalog import CatalogCreate, CatalogResponse, CatalogUpdate
from app.schemas.product import ProductResponse
from app.services.catalog_service import CatalogService
from app.services.product_service import ProductService

router = APIRouter(prefix="/catalogs", tags=["Catalogs"])


@router.get(
    "",
    response_model=list[CatalogResponse],
    summary="List catalogs",
    description="Returns a paginated list of catalogs sorted by ID ascending.",
)
def list_catalogs(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return CatalogService(db).list_catalogs_paginated(offset=offset, limit=limit)


@router.post(
    "",
    response_model=CatalogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create catalog",
    description="Creates a new catalog. Catalog name must be unique.",
    responses={409: {"description": "Catalog name already exists"}},
)
def create_catalog(payload: CatalogCreate, db: Session = Depends(get_db)):
    return CatalogService(db).create_catalog(payload)


@router.patch(
    "/{catalog_id}",
    response_model=CatalogResponse,
    summary="Update catalog fields",
    description="Partially updates a catalog by ID.",
    responses={
        404: {"description": "Catalog not found"},
        409: {"description": "Catalog name already exists"},
    },
)
def patch_catalog(catalog_id: int, payload: CatalogUpdate, db: Session = Depends(get_db)):
    return CatalogService(db).patch_catalog(catalog_id, payload)


@router.delete(
    "/{catalog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete catalog",
    description="Deletes a catalog and its related products.",
    responses={404: {"description": "Catalog not found"}},
)
def delete_catalog(catalog_id: int, db: Session = Depends(get_db)):
    CatalogService(db).delete_catalog(catalog_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{catalog_id}/products",
    response_model=list[ProductResponse],
    summary="List products in catalog",
    description="Returns a paginated list of products assigned to a specific catalog.",
    responses={404: {"description": "Catalog not found"}},
)
def list_catalog_products(
    catalog_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    CatalogService(db).get_catalog(catalog_id)
    return ProductService(db).list_products_paginated(
        catalog_id=catalog_id, offset=offset, limit=limit
    )
