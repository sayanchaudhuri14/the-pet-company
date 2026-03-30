import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.groomer import GroomerProfile
from app.models.user import User
from app.schemas.groomer import GroomerResponse, GroomerUpdate
from app.core.dependencies import require_groomer

router = APIRouter(prefix="/groomers", tags=["Groomers"])


@router.get("", response_model=list[GroomerResponse])
def list_groomers(
    # --- filters ---
    pet_type: str | None = Query(None, description="Filter by pet, e.g. 'dog'"),
    max_price: int | None = Query(None, description="Only groomers whose price_min <= this value"),
    min_experience: int | None = Query(None, description="Minimum years of experience"),
    # --- sorting ---
    sort_by: str = Query("price", description="Sort by: 'price' or 'experience'"),
    # --- pagination ---
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Public endpoint. Returns active groomers.
    Filters: pet_type, max_price, min_experience
    Sort: price (low to high) or experience (high to low)
    """
    query = db.query(GroomerProfile).filter(GroomerProfile.is_active == True)  # noqa: E712

    if pet_type:
        # Strip everything except word chars and hyphens before using in LIKE.
        # SQLAlchemy parameterises the value (preventing classical SQL injection),
        # but unsanitised input can still inject SQL LIKE wildcards (% _) that
        # cause unintended full-table scans or logic bypass.
        sanitized_pet = re.sub(r"[^\w-]", "", pet_type)
        if not sanitized_pet:
            raise HTTPException(status_code=400, detail="Invalid pet_type value")
        query = query.filter(GroomerProfile.pets_supported.like(f'%"{sanitized_pet}"%'))

    if max_price is not None:
        query = query.filter(GroomerProfile.price_min <= max_price)

    if min_experience is not None:
        query = query.filter(GroomerProfile.experience_years >= min_experience)

    if sort_by == "experience":
        query = query.order_by(GroomerProfile.experience_years.desc())
    else:
        # Default: price low to high
        query = query.order_by(GroomerProfile.price_min.asc())

    return query.offset(skip).limit(limit).all()


@router.get("/{groomer_id}", response_model=GroomerResponse)
def get_groomer(groomer_id: int, db: Session = Depends(get_db)):
    """Public endpoint. Returns a single groomer profile by id."""
    groomer = db.query(GroomerProfile).filter(GroomerProfile.id == groomer_id).first()
    if not groomer:
        raise HTTPException(status_code=404, detail="Groomer not found")
    return groomer


@router.patch("/me", response_model=GroomerResponse)
def update_my_profile(
    payload: GroomerUpdate,
    current_user: User = Depends(require_groomer),
    db: Session = Depends(get_db),
):
    """Groomer-only. Update fields on your own profile."""
    groomer = db.query(GroomerProfile).filter(
        GroomerProfile.user_id == current_user.id
    ).first()

    if not groomer:
        raise HTTPException(status_code=404, detail="Groomer profile not found")

    # Only update fields that were actually sent in the request
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(groomer, field, value)

    db.commit()
    db.refresh(groomer)
    return groomer
