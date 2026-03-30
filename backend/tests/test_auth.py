"""
Tests for auth registration — duplicate email handling and enumeration resistance.
"""

CUSTOMER_REG = {
    "email": "unique@test.com",
    "password": "testpass123!",
    "name": "Test User",
    "phone": "9000000099",
}

GROOMER_REG = {
    "email": "groomer_unique@test.com",
    "password": "testpass123!",
    "name": "Test Groomer",
    "phone": "9000000098",
    "city": "Mumbai",
    "groomer_type": "freelancer",
    "services": ["bath"],
    "pets_supported": ["dog"],
    "price_min": 200,
    "price_max": 500,
    "experience_years": 2,
}


def test_customer_registration_succeeds(client):
    r = client.post("/auth/register/customer", json=CUSTOMER_REG)
    assert r.status_code == 201
    assert r.json()["email"] == CUSTOMER_REG["email"]


def test_duplicate_customer_email_returns_409(client):
    """Registering the same customer email twice returns 409, not 400."""
    client.post("/auth/register/customer", json=CUSTOMER_REG)
    r = client.post("/auth/register/customer", json=CUSTOMER_REG)
    assert r.status_code == 409


def test_duplicate_customer_response_does_not_leak_email(client):
    """409 response body must not mention 'email' or 'registered'."""
    client.post("/auth/register/customer", json=CUSTOMER_REG)
    r = client.post("/auth/register/customer", json=CUSTOMER_REG)
    body = r.json()["detail"].lower()
    assert "email" not in body
    assert "registered" not in body


def test_groomer_registration_succeeds(client):
    r = client.post("/auth/register/groomer", json=GROOMER_REG)
    assert r.status_code == 201


def test_duplicate_groomer_email_returns_409(client):
    """Registering the same groomer email twice returns 409."""
    client.post("/auth/register/groomer", json=GROOMER_REG)
    r = client.post("/auth/register/groomer", json=GROOMER_REG)
    assert r.status_code == 409


def test_duplicate_groomer_response_does_not_leak_email(client):
    """409 response body must not mention 'email' or 'registered'."""
    client.post("/auth/register/groomer", json=GROOMER_REG)
    r = client.post("/auth/register/groomer", json=GROOMER_REG)
    body = r.json()["detail"].lower()
    assert "email" not in body
    assert "registered" not in body
