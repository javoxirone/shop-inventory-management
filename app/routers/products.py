from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import (
    ProductAssignCatalog,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=list[ProductResponse],
    summary="List products",
    description="Returns a paginated list of products sorted by ID ascending.",
)
def list_products(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return ProductService(db).list_products_paginated(offset=offset, limit=limit)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Creates a product. SKU must be unique.",
    responses={
        404: {"description": "Catalog not found when catalog_id is provided"},
        409: {"description": "SKU already exists"},
    },
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    return ProductService(db).create_product(payload)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product fields",
    description="Partially updates a product by ID.",
    responses={
        404: {"description": "Product not found"},
        409: {"description": "SKU already exists"},
    },
)
def patch_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    return ProductService(db).patch_product(product_id, payload)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete product",
    description="Deletes a product by ID.",
    responses={404: {"description": "Product not found"}},
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    ProductService(db).delete_product(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{product_id}/catalog",
    response_model=ProductResponse,
    summary="Assign product to catalog",
    description="Assigns an existing product to an existing catalog.",
    responses={
        404: {"description": "Product or catalog not found"},
    },
)
def assign_product_to_catalog(
    product_id: int,
    payload: ProductAssignCatalog,
    db: Session = Depends(get_db),
):
    return ProductService(db).assign_product_to_catalog(product_id, payload.catalog_id)


@router.delete(
    "/{product_id}/catalog",
    response_model=ProductResponse,
    summary="Remove product from catalog",
    description="Detaches the product from any catalog by setting catalog_id to null.",
    responses={404: {"description": "Product not found"}},
)
def remove_product_from_catalog(product_id: int, db: Session = Depends(get_db)):
    return ProductService(db).remove_product_from_catalog(product_id)
