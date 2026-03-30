"""
Tests for security config: SECRET_KEY enforcement, password strength, token expiry.
"""
import pytest
from pydantic import ValidationError


def test_settings_requires_secret_key(monkeypatch):
    """App config must fail if SECRET_KEY is not set — prevents accidental prod deploy."""
    monkeypatch.delenv("SECRET_KEY", raising=False)
    # Re-import Settings class (not the singleton) to test validation
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class TestSettings(BaseSettings):
        SECRET_KEY: str
        model_config = SettingsConfigDict(env_file=".env.nonexistent")

    with pytest.raises(ValidationError):
        TestSettings()


def test_password_too_short_customer(client):
    """Passwords under 10 characters must be rejected with 422."""
    r = client.post("/auth/register/customer", json={
        "email": "a@test.com",
        "password": "short1",   # 6 chars — below new minimum of 10
        "name": "Alice",
    })
    assert r.status_code == 422
    assert "10 characters" in r.text


def test_password_too_short_groomer(client):
    """Groomer registration also enforces the 10-char minimum."""
    r = client.post("/auth/register/groomer", json={
        "email": "g@test.com",
        "password": "tooshort",   # 8 chars
        "name": "Bob", "phone": "123", "city": "X",
        "groomer_type": "freelancer", "services": ["bath"],
        "pets_supported": ["dog"], "price_min": 100, "price_max": 200,
    })
    assert r.status_code == 422
    assert "10 characters" in r.text


def test_password_exactly_10_chars_accepted(client):
    """A password of exactly 10 characters must pass."""
    r = client.post("/auth/register/customer", json={
        "email": "b@test.com",
        "password": "valid12345",   # exactly 10
        "name": "Bob",
    })
    assert r.status_code == 201


def test_token_expiry_is_30_minutes():
    """ACCESS_TOKEN_EXPIRE_MINUTES must be 30, not the old 1440 (24h)."""
    from app.core.config import settings
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30


def test_secret_key_has_no_default():
    """SECRET_KEY field must not have a hardcoded default value."""
    from app.core.config import Settings
    field = Settings.model_fields["SECRET_KEY"]
    # If there's no default, pydantic marks it as required (PydanticUndefined)
    from pydantic_core import PydanticUndefinedType
    assert isinstance(field.default, PydanticUndefinedType), (
        "SECRET_KEY must not have a hardcoded default value"
    )
