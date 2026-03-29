import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class GroomerType(str, enum.Enum):
    freelancer = "freelancer"
    company = "company"


class GroomerProfile(Base):
    __tablename__ = "groomer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    city = Column(String, nullable=False)
    groomer_type = Column(Enum(GroomerType), nullable=False)

    # Stored as JSON arrays, e.g. ["bath", "haircut"] and ["dog", "cat"]
    services = Column(JSON, nullable=False, default=list)
    pets_supported = Column(JSON, nullable=False, default=list)

    price_min = Column(Integer, nullable=False)
    price_max = Column(Integer, nullable=False)
    experience_years = Column(Integer, nullable=False, default=0)

    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="groomer_profile")
    bookings = relationship("Booking", back_populates="groomer")
