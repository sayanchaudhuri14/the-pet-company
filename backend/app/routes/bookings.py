from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.groomer import GroomerProfile
from app.models.customer import CustomerProfile
from app.models.user import User, UserRole
from app.schemas.booking import BookingCreate, BookingStatusUpdate, BookingResponse
from app.core.dependencies import get_current_user, require_customer, require_groomer

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(require_customer),
    db: Session = Depends(get_db),
):
    """Customer creates a booking request for a groomer."""
    # Verify the groomer exists and is active
    groomer = db.query(GroomerProfile).filter(
        GroomerProfile.id == payload.groomer_id,
        GroomerProfile.is_active == True,  # noqa: E712
    ).first()
    if not groomer:
        raise HTTPException(status_code=404, detail="Groomer not found or inactive")

    # Get customer's profile (created at registration)
    customer = db.query(CustomerProfile).filter(
        CustomerProfile.user_id == current_user.id
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer profile not found")

    # Prevent booking yourself (if a user somehow has both roles — defensive check)
    if groomer.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot book yourself")

    # Validate the requested pet and service are in the groomer's offerings
    if payload.pet_type not in groomer.pets_supported:
        raise HTTPException(status_code=400, detail="Groomer does not support this pet type")
    if payload.service not in groomer.services:
        raise HTTPException(status_code=400, detail="Groomer does not offer this service")

    booking = Booking(
        customer_id=customer.id,
        groomer_id=groomer.id,
        pet_type=payload.pet_type,
        service=payload.service,
        scheduled_at=payload.scheduled_at,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/mine", response_model=list[BookingResponse])
def get_my_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns bookings relevant to the current user:
    - Customer: all bookings they placed
    - Groomer: all bookings assigned to them
    """
    if current_user.role == UserRole.customer:
        customer = db.query(CustomerProfile).filter(
            CustomerProfile.user_id == current_user.id
        ).first()
        if not customer:
            return []
        return (
            db.query(Booking)
            .filter(Booking.customer_id == customer.id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    else:
        groomer = db.query(GroomerProfile).filter(
            GroomerProfile.user_id == current_user.id
        ).first()
        if not groomer:
            return []
        return (
            db.query(Booking)
            .filter(Booking.groomer_id == groomer.id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns a single booking. Only the customer or groomer involved can view it."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    _assert_booking_access(booking, current_user, db)
    return booking


@router.patch("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    current_user: User = Depends(require_groomer),
    db: Session = Depends(get_db),
):
    """Groomer accepts or rejects a pending booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).with_for_update().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Ensure this booking belongs to the current groomer
    groomer = db.query(GroomerProfile).filter(
        GroomerProfile.user_id == current_user.id
    ).first()
    if not groomer or booking.groomer_id != groomer.id:
        raise HTTPException(status_code=403, detail="Not your booking")

    if booking.status != BookingStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"Booking is already '{booking.status}' and cannot be changed",
        )

    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return booking


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _assert_booking_access(booking: Booking, user: User, db: Session) -> None:
    """Raise 403 if the user is neither the customer nor the groomer for this booking."""
    if user.role == UserRole.customer:
        customer = db.query(CustomerProfile).filter(
            CustomerProfile.user_id == user.id
        ).first()
        if not customer or booking.customer_id != customer.id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        groomer = db.query(GroomerProfile).filter(
            GroomerProfile.user_id == user.id
        ).first()
        if not groomer or booking.groomer_id != groomer.id:
            raise HTTPException(status_code=403, detail="Access denied")
