from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
import app.models  # noqa: F401 — ensures all models are registered with Base
from app.routes import auth, groomers, bookings
from app.core.config import settings
from app.core.limiter import limiter  # shared singleton used by all route modules

app = FastAPI(title="ThePetCompany API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Only allow explicitly configured origins — never wildcard in production.
# Set ALLOWED_ORIGINS in .env to match your frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(groomers.router)
app.include_router(bookings.router)


@app.on_event("startup")
def create_tables():
    """Create all database tables on startup if they don't exist."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "ThePetCompany API is running"}
