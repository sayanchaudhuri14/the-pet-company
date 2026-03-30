"""
Tests that the expected database indexes exist on the models.
Uses SQLAlchemy inspector against the in-memory test DB.
"""
from sqlalchemy import inspect


def test_groomer_city_index_exists(db_session):
    inspector = inspect(db_session.bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("groomer_profiles")}
    assert "ix_groomer_city" in indexes


def test_booking_customer_id_index_exists(db_session):
    inspector = inspect(db_session.bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("bookings")}
    assert "ix_booking_customer_id" in indexes


def test_booking_groomer_id_index_exists(db_session):
    inspector = inspect(db_session.bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("bookings")}
    assert "ix_booking_groomer_id" in indexes


def test_booking_status_index_exists(db_session):
    inspector = inspect(db_session.bind)
    indexes = {idx["name"] for idx in inspector.get_indexes("bookings")}
    assert "ix_booking_status" in indexes
