from pydantic import BaseModel
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
    services: list[str] | None = None
    pets_supported: list[str] | None = None
    price_min: int | None = None
    price_max: int | None = None
    experience_years: int | None = None
    is_active: bool | None = None
