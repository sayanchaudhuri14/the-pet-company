"""
Tests for booking creation — pet/service validation against groomer's offerings.
"""
from datetime import datetime, timedelta, timezone


def _future():
    return (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()


def test_valid_booking_succeeds(client, customer_headers, groomer_id):
    """A booking with supported pet and service is created."""
    r = client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "dog",
        "service": "bath",
        "scheduled_at": _future(),
    }, headers=customer_headers)
    assert r.status_code == 201
    assert r.json()["status"] == "pending"


def test_unsupported_pet_type_returns_400(client, customer_headers, groomer_id):
    """Booking for a pet the groomer doesn't support must return 400."""
    r = client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "elephant",
        "service": "bath",
        "scheduled_at": _future(),
    }, headers=customer_headers)
    assert r.status_code == 400
    assert "pet" in r.json()["detail"].lower()


def test_unsupported_service_returns_400(client, customer_headers, groomer_id):
    """Booking for a service the groomer doesn't offer must return 400."""
    r = client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "dog",
        "service": "surgery",
        "scheduled_at": _future(),
    }, headers=customer_headers)
    assert r.status_code == 400
    assert "service" in r.json()["detail"].lower()


def test_past_scheduled_at_returns_422(client, customer_headers, groomer_id):
    """A booking with a past datetime is rejected by schema validation."""
    past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    r = client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "dog",
        "service": "bath",
        "scheduled_at": past,
    }, headers=customer_headers)
    assert r.status_code == 422


def test_booking_inactive_groomer_returns_404(client, customer_headers, groomer_id, groomer_headers):
    """Booking an inactive groomer returns 404."""
    client.patch("/groomers/me", json={"is_active": False}, headers=groomer_headers)
    r = client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "dog",
        "service": "bath",
        "scheduled_at": _future(),
    }, headers=customer_headers)
    assert r.status_code == 404
