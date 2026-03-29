from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
import app.models  # noqa: F401 — ensures all models are registered with Base
from app.routes import auth, groomers, bookings

app = FastAPI(title="ThePetCompany API", version="0.1.0")

# Allow the HTML frontend (opened as a local file or any origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
