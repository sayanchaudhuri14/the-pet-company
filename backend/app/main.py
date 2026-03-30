import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

logger = logging.getLogger(__name__)

from app.database import engine, Base
import app.models  # noqa: F401 — ensures all models are registered with Base
from app.routes import auth, groomers, bookings
from app.core.config import settings
from app.core.limiter import limiter  # shared singleton used by all route modules

app = FastAPI(title="ThePetCompany API", version="0.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all: log full traceback server-side, return opaque 500 to client."""
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

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
