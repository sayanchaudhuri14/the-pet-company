from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# SQLite database stored in the backend folder
DATABASE_URL = "sqlite:///./petcompany.db"

# connect_args is SQLite-specific: allows multiple threads to use the same connection
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Each request gets its own session, closed when the request ends
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All SQLAlchemy models inherit from this base class."""
    pass


def get_db():
    """
    FastAPI dependency that yields a DB session per request.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
