"""
Tests for groomer list query parameter validation.
- sort_by must be 'price' or 'experience' (Literal)
- max_price and min_experience must be >= 0
"""


def test_invalid_sort_by_returns_422(client):
    """sort_by with unknown value must return 422 Unprocessable Entity."""
    r = client.get("/groomers", params={"sort_by": "rating"})
    assert r.status_code == 422


def test_valid_sort_by_price(client, groomer_token):
    """sort_by=price is valid."""
    r = client.get("/groomers", params={"sort_by": "price"})
    assert r.status_code == 200


def test_valid_sort_by_experience(client, groomer_token):
    """sort_by=experience is valid."""
    r = client.get("/groomers", params={"sort_by": "experience"})
    assert r.status_code == 200


def test_negative_max_price_returns_422(client):
    """max_price=-1 must be rejected with 422."""
    r = client.get("/groomers", params={"max_price": -1})
    assert r.status_code == 422


def test_zero_max_price_is_valid(client):
    """max_price=0 is allowed (ge=0)."""
    r = client.get("/groomers", params={"max_price": 0})
    assert r.status_code == 200


def test_negative_min_experience_returns_422(client):
    """min_experience=-1 must be rejected with 422."""
    r = client.get("/groomers", params={"min_experience": -1})
    assert r.status_code == 422


def test_zero_min_experience_is_valid(client):
    """min_experience=0 is allowed (ge=0)."""
    r = client.get("/groomers", params={"min_experience": 0})
    assert r.status_code == 200
