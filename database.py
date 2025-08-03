import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings

# Database URL configuration
# Must be set for production (Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set for production deployment")

# External database (Supabase)
if DATABASE_URL.startswith("postgres://"):
    # Convert postgres:// to postgresql+psycopg:// for psycopg3
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif not DATABASE_URL.startswith("postgresql+psycopg://"):
    # Ensure we're using psycopg3
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Create database engine with proper connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # Connection pool settings
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 