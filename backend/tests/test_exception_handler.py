"""
Tests for the global unhandled exception handler.
An injected RuntimeError must return 500 with no internal details exposed.
"""
from fastapi.testclient import TestClient

from app.main import app


def test_unhandled_exception_returns_500(db_session):
    """Injected RuntimeError must return 500, not propagate to test runner."""
    @app.get("/__test_bomb__")
    async def bomb():
        raise RuntimeError("secret internal error")

    try:
        # raise_server_exceptions=False prevents TestClient from re-raising the exc
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/__test_bomb__")
        assert r.status_code == 500
    finally:
        app.routes[:] = [r for r in app.routes if getattr(r, "path", None) != "/__test_bomb__"]


def test_unhandled_exception_body_is_opaque(db_session):
    """Response must not expose the exception message or traceback."""
    @app.get("/__test_bomb2__")
    async def bomb2():
        raise RuntimeError("secret internal error")

    try:
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/__test_bomb2__")
        body = r.text
        assert "secret internal error" not in body
        assert "RuntimeError" not in body
    finally:
        app.routes[:] = [r for r in app.routes if getattr(r, "path", None) != "/__test_bomb2__"]


def test_unhandled_exception_detail_key_present(db_session):
    """Response body must contain a 'detail' key with a generic message."""
    @app.get("/__test_bomb3__")
    async def bomb3():
        raise RuntimeError("secret internal error")

    try:
        client = TestClient(app, raise_server_exceptions=False)
        r = client.get("/__test_bomb3__")
        assert "detail" in r.json()
        assert r.json()["detail"] == "An internal server error occurred."
    finally:
        app.routes[:] = [r for r in app.routes if getattr(r, "path", None) != "/__test_bomb3__"]
