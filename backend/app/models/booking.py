import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)
    groomer_id = Column(Integer, ForeignKey("groomer_profiles.id"), nullable=False)

    pet_type = Column(String, nullable=False)       # e.g. "dog", "cat"
    service = Column(String, nullable=False)         # e.g. "bath", "haircut"
    scheduled_at = Column(DateTime, nullable=False)  # requested date/time

    status = Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    customer = relationship("CustomerProfile", back_populates="bookings")
    groomer = relationship("GroomerProfile", back_populates="bookings")
