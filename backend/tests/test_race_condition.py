"""
Tests for booking status update idempotency (covers the with_for_update path).
An accepted booking cannot be subsequently rejected (sequential guard).
"""
from datetime import datetime, timedelta, timezone


def _future():
    return (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()


def _make_booking(client, customer_headers, groomer_id):
    r = client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "dog",
        "service": "bath",
        "scheduled_at": _future(),
    }, headers=customer_headers)
    assert r.status_code == 201
    return r.json()["id"]


def test_accepted_booking_cannot_be_rejected(client, customer_headers, groomer_headers, groomer_id):
    """Once accepted, a groomer cannot reject the same booking."""
    booking_id = _make_booking(client, customer_headers, groomer_id)

    # Accept first
    r = client.patch(f"/bookings/{booking_id}/status",
                     json={"status": "accepted"}, headers=groomer_headers)
    assert r.status_code == 200

    # Attempt to reject — must fail since status is no longer pending
    r = client.patch(f"/bookings/{booking_id}/status",
                     json={"status": "rejected"}, headers=groomer_headers)
    assert r.status_code == 400


def test_rejected_booking_cannot_be_accepted(client, customer_headers, groomer_headers, groomer_id):
    """Once rejected, a groomer cannot accept the same booking."""
    booking_id = _make_booking(client, customer_headers, groomer_id)

    r = client.patch(f"/bookings/{booking_id}/status",
                     json={"status": "rejected"}, headers=groomer_headers)
    assert r.status_code == 200

    r = client.patch(f"/bookings/{booking_id}/status",
                     json={"status": "accepted"}, headers=groomer_headers)
    assert r.status_code == 400


def test_cannot_set_status_to_pending(client, customer_headers, groomer_headers, groomer_id):
    """Schema prevents groomer from manually setting status back to pending."""
    booking_id = _make_booking(client, customer_headers, groomer_id)
    r = client.patch(f"/bookings/{booking_id}/status",
                     json={"status": "pending"}, headers=groomer_headers)
    assert r.status_code == 422
