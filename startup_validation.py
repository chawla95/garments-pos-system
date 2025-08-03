#!/usr/bin/env python3
"""
Startup validation script for the Garments POS System
Validates environment variables and dependencies before starting the application
"""

import os
import sys
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_environment_variables() -> Tuple[bool, List[str]]:
    """Validate required environment variables"""
    required_vars = [
        "DATABASE_URL",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def validate_database_connection() -> bool:
    """Test database connection"""
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def validate_dependencies() -> bool:
    """Validate required Python packages"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    # Special check for PostgreSQL driver
    try:
        import psycopg2
        logger.info("✅ PostgreSQL driver (psycopg2) found")
    except ImportError:
        try:
            import psycopg2_binary
            logger.info("✅ PostgreSQL driver (psycopg2-binary) found")
        except ImportError:
            missing_packages.append("psycopg2-binary")
    
    if missing_packages:
        logger.error(f"❌ Missing packages: {missing_packages}")
        return False
    
    logger.info("✅ All required packages are installed")
    return True

def main():
    """Main validation function"""
    logger.info("🔍 Starting startup validation...")
    
    # Validate environment variables
    env_valid, missing_env = validate_environment_variables()
    if not env_valid:
        logger.error(f"❌ Missing environment variables: {missing_env}")
        logger.error("Please set the required environment variables in Render dashboard")
        sys.exit(1)
    
    logger.info("✅ Environment variables validated")
    
    # Validate dependencies
    if not validate_dependencies():
        logger.error("❌ Dependencies validation failed")
        sys.exit(1)
    
    # Validate database connection
    if not validate_database_connection():
        logger.error("❌ Database connection validation failed")
        sys.exit(1)
    
    logger.info("✅ All validations passed! Application is ready to start.")
    return True

if __name__ == "__main__":
    main() 