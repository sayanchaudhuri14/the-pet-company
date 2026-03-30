"""
Tests for CORS configuration — ensures the API only allows configured origins.
"""
from app.core.config import settings


def test_allowed_origin_gets_cors_header(client):
    """A request from an allowed origin must receive the CORS header."""
    allowed = settings.ALLOWED_ORIGINS[0]
    r = client.options(
        "/auth/login",
        headers={
            "Origin": allowed,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" in r.headers
    assert r.headers["access-control-allow-origin"] == allowed


def test_unknown_origin_does_not_get_cors_header(client):
    """A request from an unknown origin must NOT receive an Allow-Origin header."""
    r = client.options(
        "/auth/login",
        headers={
            "Origin": "https://evil-attacker.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    # The header should be absent or not echo back the evil origin
    origin_header = r.headers.get("access-control-allow-origin", "")
    assert "evil-attacker.com" not in origin_header


def test_wildcard_not_in_allowed_origins():
    """Ensure no wildcard (*) is in the ALLOWED_ORIGINS config."""
    assert "*" not in settings.ALLOWED_ORIGINS, (
        "Wildcard '*' must not appear in ALLOWED_ORIGINS — it bypasses CORS protection"
    )


def test_only_required_methods_allowed(client):
    """Preflight response must only expose the restricted method list."""
    allowed = settings.ALLOWED_ORIGINS[0]
    r = client.options(
        "/groomers",
        headers={
            "Origin": allowed,
            "Access-Control-Request-Method": "GET",
        },
    )
    allowed_methods = r.headers.get("access-control-allow-methods", "")
    # DELETE should not be in allowed methods
    assert "DELETE" not in allowed_methods.upper()
