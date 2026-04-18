from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
        description="Display name of the product.",
        examples=["Mechanical Keyboard"],
    )
    sku: str = Field(
        min_length=1,
        max_length=80,
        description="Unique stock keeping unit identifier.",
        examples=["KB-001"],
    )
    price: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Unit price with 2 decimal precision.",
        examples=["49.99"],
    )
    quantity: int = Field(
        ge=0,
        default=0,
        description="Current stock quantity.",
        examples=[25],
    )


class ProductCreate(ProductBase):
    catalog_id: int | None = Field(
        default=None,
        description="Optional catalog ID to attach at creation time.",
        examples=[1],
    )


class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="New product name.",
        examples=["Wireless Mouse"],
    )
    sku: str | None = Field(
        default=None,
        min_length=1,
        max_length=80,
        description="New SKU value.",
        examples=["MS-101"],
    )
    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
        description="Updated product unit price.",
        examples=["39.50"],
    )
    quantity: int | None = Field(
        default=None,
        ge=0,
        description="Updated stock quantity.",
        examples=[42],
    )


class ProductAssignCatalog(BaseModel):
    catalog_id: int = Field(
        description="Target catalog ID for assignment.",
        examples=[2],
    )


class ProductResponse(ProductBase):
    id: int
    catalog_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
