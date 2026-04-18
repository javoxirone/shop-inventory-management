from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.catalog import Catalog
from app.schemas.catalog import CatalogCreate, CatalogUpdate
from app.services.db_errors import with_integrity_handling


class CatalogService:
    """Service layer for catalog-related operations."""

    def __init__(self, db: Session):
        """Initialize the service with a database session.

        Args:
            db: Active SQLAlchemy session.
        """
        self.db = db

    def list_catalogs(self) -> list[Catalog]:
        """Return all catalogs sorted by ID.

        Returns:
            List[Catalog]: Catalog records.
        """
        return self.db.query(Catalog).order_by(Catalog.id.asc()).all()

    def list_catalogs_paginated(self, offset: int, limit: int) -> list[Catalog]:
        """Return a paginated catalog list sorted by ID.

        Args:
            offset: Number of rows to skip.
            limit: Maximum number of rows to return.

        Returns:
            List[Catalog]: Paginated catalog records.
        """
        return self.db.query(Catalog).order_by(Catalog.id.asc()).offset(offset).limit(limit).all()

    def get_catalog(self, catalog_id: int) -> Catalog:
        """Fetch one catalog by ID.

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

    def create_catalog(self, payload: CatalogCreate) -> Catalog:
        """Create a catalog.

        Args:
            payload: Input data for the catalog.

        Returns:
            Catalog: Newly created catalog.

        Raises:
            HTTPException: If a catalog with the same name already exists.
        """
        catalog = Catalog(name=payload.name, description=payload.description)
        self.db.add(catalog)

        def _commit() -> Catalog:
            self.db.commit()
            return catalog

        try:
            with_integrity_handling(_commit, "A catalog with this name already exists")
        except HTTPException:
            self.db.rollback()
            raise
        self.db.refresh(catalog)
        return catalog

    def patch_catalog(self, catalog_id: int, payload: CatalogUpdate) -> Catalog:
        """Partially update an existing catalog.

        Args:
            catalog_id: Catalog identifier.
            payload: Partial update payload.

        Returns:
            Catalog: Updated catalog.

        Raises:
            HTTPException: If the catalog does not exist or name is duplicated.
        """
        catalog = self.get_catalog(catalog_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(catalog, field, value)

        def _commit() -> Catalog:
            self.db.commit()
            return catalog

        try:
            with_integrity_handling(_commit, "A catalog with this name already exists")
        except HTTPException:
            self.db.rollback()
            raise
        self.db.refresh(catalog)
        return catalog

    def delete_catalog(self, catalog_id: int) -> None:
        """Delete a catalog by ID.

        Args:
            catalog_id: Catalog identifier.

        Raises:
            HTTPException: If the catalog does not exist.
        """
        catalog = self.get_catalog(catalog_id)
        self.db.delete(catalog)
        self.db.commit()
