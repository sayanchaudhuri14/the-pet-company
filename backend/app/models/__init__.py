# Import all models here so SQLAlchemy's Base.metadata knows about every table.
# This is required for create_all() to work correctly.
from app.models.user import User, UserRole
from app.models.groomer import GroomerProfile, GroomerType
from app.models.customer import CustomerProfile
from app.models.booking import Booking, BookingStatus
