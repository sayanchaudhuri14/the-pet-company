"""
Tests for schema-level validation: list length limits, numeric ge=0,
and cross-field price_max >= price_min on GroomerUpdate.
"""
import pytest
from pydantic import ValidationError

from app.schemas.auth import RegisterGroomer
from app.schemas.groomer import GroomerUpdate

VALID_GROOMER = {
    "email": "g@test.com",
    "password": "testpass123!",
    "name": "Test",
    "phone": "9000000001",
    "city": "Bangalore",
    "groomer_type": "freelancer",
    "services": ["bath"],
    "pets_supported": ["dog"],
    "price_min": 300,
    "price_max": 700,
    "experience_years": 3,
}


# ---------------------------------------------------------------------------
# RegisterGroomer — services / pets_supported list length
# ---------------------------------------------------------------------------

def test_register_groomer_empty_services_rejected():
    data = {**VALID_GROOMER, "services": []}
    with pytest.raises(ValidationError):
        RegisterGroomer(**data)


def test_register_groomer_21_services_rejected():
    data = {**VALID_GROOMER, "services": [f"svc{i}" for i in range(21)]}
    with pytest.raises(ValidationError):
        RegisterGroomer(**data)


def test_register_groomer_20_services_accepted():
    data = {**VALID_GROOMER, "services": [f"svc{i}" for i in range(20)]}
    r = RegisterGroomer(**data)
    assert len(r.services) == 20


def test_register_groomer_empty_pets_rejected():
    data = {**VALID_GROOMER, "pets_supported": []}
    with pytest.raises(ValidationError):
        RegisterGroomer(**data)


def test_register_groomer_negative_price_min_rejected():
    data = {**VALID_GROOMER, "price_min": -1}
    with pytest.raises(ValidationError):
        RegisterGroomer(**data)


def test_register_groomer_negative_experience_rejected():
    data = {**VALID_GROOMER, "experience_years": -1}
    with pytest.raises(ValidationError):
        RegisterGroomer(**data)


# ---------------------------------------------------------------------------
# GroomerUpdate — cross-field price validation
# ---------------------------------------------------------------------------

def test_groomer_update_price_max_less_than_price_min_rejected():
    with pytest.raises(ValidationError):
        GroomerUpdate(price_min=700, price_max=300)


def test_groomer_update_price_max_equal_price_min_accepted():
    u = GroomerUpdate(price_min=500, price_max=500)
    assert u.price_min == u.price_max


def test_groomer_update_only_price_max_no_error():
    """Sending only price_max without price_min should not raise (no comparison possible)."""
    u = GroomerUpdate(price_max=500)
    assert u.price_max == 500


def test_groomer_update_negative_price_rejected():
    with pytest.raises(ValidationError):
        GroomerUpdate(price_min=-100)


def test_groomer_update_21_services_rejected():
    with pytest.raises(ValidationError):
        GroomerUpdate(services=[f"svc{i}" for i in range(21)])


def test_groomer_update_empty_services_rejected():
    with pytest.raises(ValidationError):
        GroomerUpdate(services=[])
