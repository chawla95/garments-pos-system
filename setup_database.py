#!/usr/bin/env python3
"""
Database setup script for the Garments POS System
Initializes database tables and creates initial data
"""

import os
import sys
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Setup database tables and initial data"""
    try:
        from database import engine, SessionLocal
        from models import Base
        import auth
        import models
        
        logger.info("🔧 Setting up database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
        
        # Check if admin user exists
        db = SessionLocal()
        try:
            admin_user = db.query(models.User).filter(models.User.username == "admin").first()
            
            if not admin_user:
                logger.info("👤 Creating admin user...")
                
                # Create admin user
                admin_user = models.User(
                    username="admin",
                    email="admin@garments-pos.com",
                    full_name="System Administrator",
                    role="admin",
                    is_active=True
                )
                
                # Hash password
                admin_user.hashed_password = auth.get_password_hash("admin123")
                
                db.add(admin_user)
                db.commit()
                logger.info("✅ Admin user created (username: admin, password: admin123)")
            else:
                logger.info("✅ Admin user already exists")
                
        except Exception as e:
            logger.error(f"❌ Error creating admin user: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("✅ Database setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting database setup...")
    
    if setup_database():
        logger.info("🎉 Database setup completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 