#!/usr/bin/env python3
"""
Create Admin User for Garments POS System
Creates the initial admin user for the system
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """Create admin user"""
    try:
        from database import SessionLocal
        from models import User, UserRole
        import auth
        
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            logger.info("👤 Creating admin user...")
            
            admin_user = User(
                username="admin",
                email="admin@garments-pos.com",
                hashed_password=auth.get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            logger.info("✅ Admin user created successfully")
            logger.info("📋 Login credentials: admin / admin123")
        else:
            logger.info("✅ Admin user already exists")
            
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        return False

def main():
    """Main function"""
    logger.info("🚀 Creating admin user...")
    
    if create_admin_user():
        logger.info("🎉 Admin user setup completed!")
        logger.info("\n📋 Default credentials:")
        logger.info("   Username: admin")
        logger.info("   Password: admin123")
        logger.info("\n⚠️  Remember to change the password after first login!")
    else:
        logger.error("❌ Failed to create admin user")
        sys.exit(1)

if __name__ == "__main__":
    main() 