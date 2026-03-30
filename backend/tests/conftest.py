"""
Shared pytest fixtures for ThePetCompany test suite.

Every test gets:
- An isolated in-memory SQLite DB (created fresh, dropped after each test)
- A TestClient wired to that DB via dependency override
- Convenience fixtures for a registered customer and groomer with valid tokens
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set SECRET_KEY before importing app so pydantic-settings validation passes
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production")

from app.main import app  # noqa: E402 — must come after env var is set
from app.database import Base, get_db  # noqa: E402
from app.core.limiter import limiter  # noqa: E402 — shared singleton, reset per test

TEST_DATABASE_URL = "sqlite:///:memory:"

CUSTOMER_EMAIL = "customer@test.com"
CUSTOMER_PASSWORD = "testpass123!"
GROOMER_EMAIL = "groomer@test.com"
GROOMER_PASSWORD = "testpass123!"


@pytest.fixture(scope="function")
def db_session():
    """Fresh in-memory SQLite DB per test. Dropped after the test finishes."""
    # StaticPool forces all SQLAlchemy connections to reuse the SAME underlying
    # sqlite3 connection, so tables created by create_all() are visible to every
    # subsequent query in the same test (in-memory DBs are per-connection by default).
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """TestClient wired to the isolated test DB. Cleans up overrides after each test."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    # Reset rate limiter state so each test starts with a clean counter.
    # Without this, tests that hit rate-limited endpoints accumulate counts
    # across tests and cause fixture setup (register/login) to get 429s.
    limiter.reset()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Convenience fixtures — pre-registered users with valid JWT tokens
# ---------------------------------------------------------------------------

CUSTOMER_PAYLOAD = {
    "email": CUSTOMER_EMAIL,
    "password": CUSTOMER_PASSWORD,
    "name": "Test Customer",
    "phone": "9000000001",
}

GROOMER_PAYLOAD = {
    "email": GROOMER_EMAIL,
    "password": GROOMER_PASSWORD,
    "name": "Test Groomer",
    "phone": "9000000002",
    "city": "Bangalore",
    "groomer_type": "freelancer",
    "services": ["bath", "haircut"],
    "pets_supported": ["dog", "cat"],
    "price_min": 300,
    "price_max": 700,
    "experience_years": 3,
}


@pytest.fixture(scope="function")
def customer_token(client) -> str:
    client.post("/auth/register/customer", json=CUSTOMER_PAYLOAD)
    r = client.post("/auth/login", json={
        "email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD,
    })
    return r.json()["access_token"]


@pytest.fixture(scope="function")
def groomer_token(client) -> str:
    client.post("/auth/register/groomer", json=GROOMER_PAYLOAD)
    r = client.post("/auth/login", json={
        "email": GROOMER_EMAIL, "password": GROOMER_PASSWORD,
    })
    return r.json()["access_token"]


@pytest.fixture(scope="function")
def customer_headers(customer_token) -> dict:
    return {"Authorization": f"Bearer {customer_token}"}


@pytest.fixture(scope="function")
def groomer_headers(groomer_token) -> dict:
    return {"Authorization": f"Bearer {groomer_token}"}


@pytest.fixture(scope="function")
def groomer_id(client, groomer_token) -> int:
    """Returns the groomer profile id of the registered test groomer."""
    r = client.get("/groomers")
    return r.json()[0]["id"]
