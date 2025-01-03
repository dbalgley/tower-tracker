# database.py
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define the base model for SQLAlchemy ORM
Base = declarative_base()

# Create the database engine
DATABASE_URL = "sqlite:///game_stats.db"  # Replace with your actual database URL
engine = create_engine(DATABASE_URL, echo=False)  # Set echo=True for debugging

# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
