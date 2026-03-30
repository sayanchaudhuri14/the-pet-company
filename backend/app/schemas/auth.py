from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.user import UserRole


class RegisterCustomer(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        return v


class RegisterGroomer(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    city: str
    groomer_type: str                                                   # "freelancer" or "company"
    services: list[str] = Field(min_length=1, max_length=20)           # e.g. ["bath", "haircut"]
    pets_supported: list[str] = Field(min_length=1, max_length=20)     # e.g. ["dog", "cat"]
    price_min: int = Field(ge=0)
    price_max: int = Field(ge=0)
    experience_years: int = Field(default=0, ge=0)

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Password must be at least 10 characters")
        return v

    @field_validator("price_max")
    @classmethod
    def price_range_valid(cls, v: int, info) -> int:
        if "price_min" in info.data and v < info.data["price_min"]:
            raise ValueError("price_max must be >= price_min")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole

    model_config = {"from_attributes": True}
