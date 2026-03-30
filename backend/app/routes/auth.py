from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.groomer import GroomerProfile, GroomerType
from app.models.customer import CustomerProfile
from app.schemas.auth import (
    RegisterCustomer,
    RegisterGroomer,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.core.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/customer", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register_customer(request: Request, payload: RegisterCustomer, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.customer,
    )
    db.add(user)
    db.flush()  # assigns user.id without committing

    profile = CustomerProfile(
        user_id=user.id,
        name=payload.name,
        phone=payload.phone,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register/groomer", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register_groomer(request: Request, payload: RegisterGroomer, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.groomer,
    )
    db.add(user)
    db.flush()

    profile = GroomerProfile(
        user_id=user.id,
        name=payload.name,
        phone=payload.phone,
        city=payload.city,
        groomer_type=GroomerType(payload.groomer_type),
        services=payload.services,
        pets_supported=payload.pets_supported,
        price_min=payload.price_min,
        price_max=payload.price_max,
        experience_years=payload.experience_years,
    )
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the currently logged-in user's info."""
    return current_user
