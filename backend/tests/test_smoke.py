"""Smoke tests — verifies the test infrastructure itself is wired correctly."""


def test_health_check(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_customer_fixture(client, customer_headers):
    r = client.get("/auth/me", headers=customer_headers)
    assert r.status_code == 200
    assert r.json()["role"] == "customer"


def test_groomer_fixture(client, groomer_headers):
    r = client.get("/auth/me", headers=groomer_headers)
    assert r.status_code == 200
    assert r.json()["role"] == "groomer"


def test_db_isolation(client):
    """Each test should start with a clean DB — no users from other tests."""
    r = client.get("/groomers")
    assert r.status_code == 200
    assert r.json() == []
