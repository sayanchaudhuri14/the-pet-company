"""
Tests for GET /bookings/mine pagination (skip/limit).
"""
from datetime import datetime, timedelta, timezone


def _future(offset_hours=2):
    return (datetime.now(timezone.utc) + timedelta(hours=offset_hours)).isoformat()


def _create_booking(client, headers, groomer_id, offset_hours):
    return client.post("/bookings", json={
        "groomer_id": groomer_id,
        "pet_type": "dog",
        "service": "bath",
        "scheduled_at": _future(offset_hours),
    }, headers=headers)


def test_default_limit_returns_at_most_20(client, customer_headers, groomer_id):
    """When 25 bookings exist, default limit=20 returns exactly 20."""
    for i in range(25):
        _create_booking(client, customer_headers, groomer_id, offset_hours=2 + i)

    r = client.get("/bookings/mine", headers=customer_headers)
    assert r.status_code == 200
    assert len(r.json()) == 20


def test_custom_limit_respected(client, customer_headers, groomer_id):
    """limit=5 returns only 5 bookings."""
    for i in range(10):
        _create_booking(client, customer_headers, groomer_id, offset_hours=2 + i)

    r = client.get("/bookings/mine", params={"limit": 5}, headers=customer_headers)
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_limit_over_100_returns_422(client, customer_headers):
    """limit=101 exceeds max and must return 422."""
    r = client.get("/bookings/mine", params={"limit": 101}, headers=customer_headers)
    assert r.status_code == 422


def test_negative_skip_returns_422(client, customer_headers):
    """skip=-1 must return 422."""
    r = client.get("/bookings/mine", params={"skip": -1}, headers=customer_headers)
    assert r.status_code == 422


def test_skip_offsets_results(client, customer_headers, groomer_id):
    """skip=3 skips the 3 most recent bookings."""
    for i in range(5):
        _create_booking(client, customer_headers, groomer_id, offset_hours=2 + i)

    all_r = client.get("/bookings/mine", params={"limit": 5}, headers=customer_headers)
    skipped_r = client.get("/bookings/mine", params={"skip": 3, "limit": 5}, headers=customer_headers)

    all_ids = [b["id"] for b in all_r.json()]
    skipped_ids = [b["id"] for b in skipped_r.json()]

    assert len(skipped_ids) == 2
    assert skipped_ids == all_ids[3:]
