"""
Tests that structured log events fire correctly on login success/failure.
Uses structlog.testing.capture_logs() — no actual log output needed.
"""
import structlog.testing


GROOMER_EMAIL = "groomer@test.com"
GROOMER_PASSWORD = "testpass123!"


def test_login_success_emits_structured_event(client, groomer_token):
    """Successful login emits auth.login.success with user_id and role."""
    with structlog.testing.capture_logs() as cap_logs:
        r = client.post("/auth/login", json={
            "email": GROOMER_EMAIL,
            "password": GROOMER_PASSWORD,
        })
    assert r.status_code == 200
    success_events = [e for e in cap_logs if e.get("event") == "auth.login.success"]
    assert len(success_events) == 1
    assert "user_id" in success_events[0]
    assert "role" in success_events[0]


def test_login_failure_emits_structured_event(client):
    """Failed login emits auth.login.failure with the attempted email."""
    with structlog.testing.capture_logs() as cap_logs:
        r = client.post("/auth/login", json={
            "email": "nobody@test.com",
            "password": "wrongpass123!",
        })
    assert r.status_code == 401
    failure_events = [e for e in cap_logs if e.get("event") == "auth.login.failure"]
    assert len(failure_events) == 1
    assert failure_events[0]["email"] == "nobody@test.com"
