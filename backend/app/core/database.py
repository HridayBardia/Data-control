from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Engine configuration with settings tailored for enterprise load:
# pool_pre_ping prevents using disconnected sessions, pool_size sets limit, max_overflow allows burst
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator:
    """
    FastAPI dependency that provides a transactional database session.
    Automatically closes the session after request lifecycle completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
