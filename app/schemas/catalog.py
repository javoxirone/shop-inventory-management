from pydantic import BaseModel, ConfigDict, Field


class CatalogBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=120,
        description="Unique catalog name.",
        examples=["Electronics"],
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="Short description of the catalog.",
        examples=["Gadgets, phones, and accessories"],
    )


class CatalogCreate(CatalogBase):
    pass


class CatalogUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="New catalog name.",
        examples=["Home Appliances"],
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="New catalog description.",
        examples=["Kitchen and household items"],
    )


class CatalogResponse(CatalogBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
