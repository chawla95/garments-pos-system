import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Database URL configuration
# Priority: DATABASE_URL > individual components
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # External database (Railway, Supabase, etc.)
    if DATABASE_URL.startswith("postgres://"):
        # Convert postgres:// to postgresql:// for SQLAlchemy
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Local SQLite database (fallback)
    SQLALCHEMY_DATABASE_URL = "sqlite:///./pos_system.db"

# Create database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # For SQLite, enable foreign key support
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
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