"""
Tests for rate limiting on auth endpoints.
"""


def test_login_rate_limit_triggers_after_10_requests(client):
    """11th login attempt from same IP within a minute must return 429."""
    payload = {"email": "x@test.com", "password": "wrongpassword123"}

    responses = [
        client.post("/auth/login", json=payload)
        for _ in range(11)
    ]

    status_codes = [r.status_code for r in responses]
    # First 10 should be 401 (invalid credentials), 11th should be 429
    assert all(c == 401 for c in status_codes[:10]), (
        f"Expected 401 for first 10 requests, got: {status_codes[:10]}"
    )
    assert status_codes[10] == 429, (
        f"Expected 429 on 11th request, got: {status_codes[10]}"
    )


def test_login_429_has_error_body(client):
    """Rate limit response must return a JSON body with error detail."""
    payload = {"email": "x@test.com", "password": "wrongpassword123"}

    responses = [client.post("/auth/login", json=payload) for _ in range(11)]
    rate_limited = responses[10]

    assert rate_limited.status_code == 429
    # slowapi returns JSON with error detail
    assert rate_limited.headers.get("content-type", "").startswith("application/json")


def test_register_customer_rate_limit_triggers_after_5_requests(client):
    """6th register attempt from same IP within a minute must return 429."""
    responses = []
    for i in range(6):
        responses.append(client.post("/auth/register/customer", json={
            "email": f"user{i}@test.com",
            "password": "validpass123!",
            "name": f"User {i}",
        }))

    status_codes = [r.status_code for r in responses]
    # First 5 should succeed (201), 6th should be 429
    assert all(c == 201 for c in status_codes[:5]), (
        f"Expected 201 for first 5 requests, got: {status_codes[:5]}"
    )
    assert status_codes[5] == 429, (
        f"Expected 429 on 6th request, got: {status_codes[5]}"
    )


def test_register_groomer_rate_limit_triggers_after_5_requests(client):
    """6th groomer register attempt must return 429."""
    base = {
        "password": "validpass123!",
        "phone": "9000000001",
        "city": "Bangalore",
        "groomer_type": "freelancer",
        "services": ["bath"],
        "pets_supported": ["dog"],
        "price_min": 300,
        "price_max": 700,
        "experience_years": 2,
    }
    responses = []
    for i in range(6):
        responses.append(client.post("/auth/register/groomer", json={
            **base,
            "email": f"groomer{i}@test.com",
            "name": f"Groomer {i}",
        }))

    status_codes = [r.status_code for r in responses]
    assert all(c == 201 for c in status_codes[:5])
    assert status_codes[5] == 429
