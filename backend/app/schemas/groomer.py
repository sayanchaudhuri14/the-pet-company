from pydantic import BaseModel, Field, model_validator
from app.models.groomer import GroomerType


class GroomerResponse(BaseModel):
    """Returned when listing or fetching a single groomer."""
    id: int
    user_id: int
    name: str
    phone: str
    city: str
    groomer_type: GroomerType
    services: list[str]
    pets_supported: list[str]
    price_min: int
    price_max: int
    experience_years: int
    is_active: bool

    model_config = {"from_attributes": True}


class GroomerUpdate(BaseModel):
    """Groomers can update their own profile fields (all optional)."""
    name: str | None = None
    phone: str | None = None
    city: str | None = None
    services: list[str] | None = Field(default=None, min_length=1, max_length=20)
    pets_supported: list[str] | None = Field(default=None, min_length=1, max_length=20)
    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)
    experience_years: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def price_max_gte_price_min(self) -> "GroomerUpdate":
        if self.price_min is not None and self.price_max is not None:
            if self.price_max < self.price_min:
                raise ValueError("price_max must be >= price_min")
        return self
