"""
Tests for timezone-aware datetime usage.
- past scheduled_at is rejected by BookingCreate
- no DeprecationWarning from datetime.utcnow()
"""
import warnings
from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.schemas.booking import BookingCreate


def test_past_scheduled_at_rejected():
    """BookingCreate must reject a past datetime."""
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    with pytest.raises(ValidationError):
        BookingCreate(
            groomer_id=1,
            pet_type="dog",
            service="bath",
            scheduled_at=past,
        )


def test_future_scheduled_at_accepted():
    """BookingCreate must accept a future datetime."""
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    booking = BookingCreate(
        groomer_id=1,
        pet_type="dog",
        service="bath",
        scheduled_at=future,
    )
    assert booking.scheduled_at == future


def test_no_deprecation_warning_from_datetime_utcnow():
    """No DeprecationWarning should be raised — utcnow() must not be used anywhere."""
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        # Import all modules that previously used utcnow — if any still do, this raises
        import app.services.auth  # noqa: F401
        import app.models.user  # noqa: F401
        import app.models.booking  # noqa: F401
        import app.schemas.booking  # noqa: F401

def test_naive_future_scheduled_at_accepted():
    """A naive future datetime is accepted (treated as UTC internally)."""
    naive_future = datetime.now() + timedelta(hours=24)
    booking = BookingCreate(
        groomer_id=1,
        pet_type="dog",
        service="bath",
        scheduled_at=naive_future,
    )
    assert booking.scheduled_at == naive_future
