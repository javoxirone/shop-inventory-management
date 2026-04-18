from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.catalog import Catalog
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.db_errors import with_integrity_handling


class ProductService:
    """Service layer for product-related operations."""

    def __init__(self, db: Session):
        """Initialize the service with a database session.

        Args:
            db: Active SQLAlchemy session.
        """
        self.db = db

    def list_products(self, catalog_id: int | None = None) -> list[Product]:
        """Return products, optionally filtered by catalog.

        Args:
            catalog_id: Optional catalog identifier filter.

        Returns:
            List[Product]: Product records sorted by ID.
        """
        query = self.db.query(Product)
        if catalog_id is not None:
            query = query.filter(Product.catalog_id == catalog_id)
        return query.order_by(Product.id.asc()).all()

    def list_products_paginated(
        self, offset: int, limit: int, catalog_id: int | None = None
    ) -> list[Product]:
        """Return a paginated product list with optional catalog filter.

        Args:
            offset: Number of rows to skip.
            limit: Maximum number of rows to return.
            catalog_id: Optional catalog identifier filter.

        Returns:
            List[Product]: Paginated product records sorted by ID.
        """
        query = self.db.query(Product)
        if catalog_id is not None:
            query = query.filter(Product.catalog_id == catalog_id)
        return query.order_by(Product.id.asc()).offset(offset).limit(limit).all()

    def get_product(self, product_id: int) -> Product:
        """Fetch one product by ID.

        Args:
            product_id: Product identifier.

        Returns:
            Product: Matching product record.

        Raises:
            HTTPException: If the product does not exist.
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def create_product(self, payload: ProductCreate) -> Product:
        """Create a product.

        Args:
            payload: Input data for the product.

        Returns:
            Product: Newly created product.

        Raises:
            HTTPException: If catalog does not exist or SKU is duplicated.
        """
        if payload.catalog_id is not None:
            self._require_catalog(payload.catalog_id)

        product = Product(**payload.model_dump())
        self.db.add(product)

        def _commit() -> Product:
            self.db.commit()
            return product

        try:
            with_integrity_handling(_commit, "A product with this SKU already exists")
        except HTTPException:
            self.db.rollback()
            raise
        self.db.refresh(product)
        return product

    def patch_product(self, product_id: int, payload: ProductUpdate) -> Product:
        """Partially update an existing product.

        Args:
            product_id: Product identifier.
            payload: Partial update payload.

        Returns:
            Product: Updated product.

        Raises:
            HTTPException: If product does not exist or SKU is duplicated.
        """
        product = self.get_product(product_id)
        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(product, field, value)

        def _commit() -> Product:
            self.db.commit()
            return product

        try:
            with_integrity_handling(_commit, "A product with this SKU already exists")
        except HTTPException:
            self.db.rollback()
            raise
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> None:
        """Delete a product by ID.

        Args:
            product_id: Product identifier.

        Raises:
            HTTPException: If the product does not exist.
        """
        product = self.get_product(product_id)
        self.db.delete(product)
        self.db.commit()

    def assign_product_to_catalog(self, product_id: int, catalog_id: int) -> Product:
        """Assign a product to a catalog.

        Args:
            product_id: Product identifier.
            catalog_id: Catalog identifier.

        Returns:
            Product: Updated product with new catalog relation.

        Raises:
            HTTPException: If product or catalog does not exist.
        """
        product = self.get_product(product_id)
        self._require_catalog(catalog_id)
        product.catalog_id = catalog_id
        self.db.commit()
        self.db.refresh(product)
        return product

    def remove_product_from_catalog(self, product_id: int) -> Product:
        """Remove catalog assignment from a product.

        Args:
            product_id: Product identifier.

        Returns:
            Product: Updated product with no catalog assignment.

        Raises:
            HTTPException: If the product does not exist.
        """
        product = self.get_product(product_id)
        product.catalog_id = None
        self.db.commit()
        self.db.refresh(product)
        return product

    def _require_catalog(self, catalog_id: int) -> Catalog:
        """Ensure a catalog exists before relation operations.

        Args:
            catalog_id: Catalog identifier.

        Returns:
            Catalog: Matching catalog record.

        Raises:
            HTTPException: If the catalog does not exist.
        """
        catalog = self.db.query(Catalog).filter(Catalog.id == catalog_id).first()
        if catalog is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog not found")
        return catalog
