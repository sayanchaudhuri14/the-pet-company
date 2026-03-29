from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    """Customer submits this to request a booking."""
    groomer_id: int
    pet_type: str    # e.g. "dog"
    service: str     # e.g. "bath"
    scheduled_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.utcnow():
            raise ValueError("scheduled_at must be a future date/time")
        return v


class BookingStatusUpdate(BaseModel):
    """Groomer uses this to accept or reject a booking."""
    status: BookingStatus

    @field_validator("status")
    @classmethod
    def cannot_set_pending(cls, v: BookingStatus) -> BookingStatus:
        if v == BookingStatus.pending:
            raise ValueError("Cannot manually set status back to pending")
        return v


class BookingResponse(BaseModel):
    """Returned when fetching bookings."""
    id: int
    customer_id: int
    groomer_id: int
    pet_type: str
    service: str
    scheduled_at: datetime
    status: BookingStatus
    created_at: datetime

    model_config = {"from_attributes": True}
