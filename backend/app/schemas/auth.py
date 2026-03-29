from pydantic import BaseModel, EmailStr, field_validator
from app.models.user import UserRole


class RegisterCustomer(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class RegisterGroomer(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str
    city: str
    groomer_type: str          # "freelancer" or "company"
    services: list[str]        # e.g. ["bath", "haircut"]
    pets_supported: list[str]  # e.g. ["dog", "cat"]
    price_min: int
    price_max: int
    experience_years: int = 0

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
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
