import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Database URL configuration
# Must be set for production (Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set for production deployment")

# External database (Supabase)
if DATABASE_URL.startswith("postgres://"):
    # Convert postgres:// to postgresql+asyncpg:// for asyncpg
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif not DATABASE_URL.startswith("postgresql+asyncpg://"):
    # Ensure we're using asyncpg
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

SQLALCHEMY_DATABASE_URL = DATABASE_URL

# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # PostgreSQL connection settings
    pool_pre_ping=True,
    pool_recycle=300
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 