#!/usr/bin/env python3
"""
Supabase Setup Script for Garments POS System
Configures your existing Supabase project for the POS system
"""

import os
import sys
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_supabase_connection_string() -> Optional[str]:
    """Get Supabase connection string from user"""
    print("\n🔗 Supabase Connection String Setup")
    print("=" * 40)
    
    print("\nTo get your Supabase connection string:")
    print("1. Go to your Supabase project dashboard")
    print("2. Click 'Settings' (gear icon) → 'Database'")
    print("3. Scroll down to 'Connection string' section")
    print("4. Copy the 'URI' connection string")
    print("5. It should look like: postgresql://postgres:[password]@[host]:5432/postgres")
    
    connection_string = input("\nEnter your Supabase connection string: ").strip()
    
    if not connection_string:
        logger.error("❌ Connection string is required")
        return None
    
    # Validate connection string format
    if not connection_string.startswith(("postgresql://", "postgres://")):
        logger.error("❌ Invalid connection string format. Should start with postgresql:// or postgres://")
        return None
    
    return connection_string

def test_database_connection(connection_string: str) -> bool:
    """Test the database connection"""
    try:
        # Temporarily set the environment variable
        os.environ["DATABASE_URL"] = connection_string
        
        # Import and test database connection
        from database import engine
        
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            version = result.fetchone()[0]
            logger.info(f"✅ Database connection successful!")
            logger.info(f"📊 PostgreSQL version: {version}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def create_environment_file(connection_string: str):
    """Create a .env file with the connection string"""
    env_content = f"""# Garments POS System - Environment Variables
# Copy these to your Render environment variables

# Database Configuration
DATABASE_URL={connection_string}

# Security Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production

# Application Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Shop Configuration
SHOP_NAME=Your Garments Store
SHOP_ADDRESS=123 Main Street, City, State 12345
SHOP_PHONE=+91-9876543210
SHOP_EMAIL=info@yourstore.com
SHOP_GSTIN=22AAAAA0000A1Z5
DEFAULT_GST_RATE=12.0
DEFAULT_CURRENCY=INR

# WhatsApp Configuration (Optional)
INTERAKT_API_KEY=
INTERAKT_API_SECRET=
INTERAKT_PHONE_NUMBER_ID=
INTERAKT_BUSINESS_ACCOUNT_ID=
"""
    
    try:
        with open(".env.example", "w") as f:
            f.write(env_content)
        logger.info("✅ Created .env.example file with your configuration")
        logger.info("📝 Review and update the values as needed")
    except Exception as e:
        logger.error(f"❌ Failed to create .env.example: {e}")

def setup_database_tables():
    """Create database tables"""
    try:
        from database import engine
        from models import Base
        
        logger.info("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def create_initial_data():
    """Create initial admin user"""
    try:
        from database import SessionLocal
        from models import User
        import auth
        
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            logger.info("👤 Creating admin user...")
            
            admin_user = User(
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
            logger.info("✅ Admin user created successfully")
            logger.info("📋 Login credentials: admin / admin123")
        else:
            logger.info("✅ Admin user already exists")
            
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create initial data: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Garments POS System - Supabase Setup")
    print("=" * 50)
    
    # Get connection string
    connection_string = get_supabase_connection_string()
    if not connection_string:
        sys.exit(1)
    
    # Test connection
    if not test_database_connection(connection_string):
        sys.exit(1)
    
    # Create environment file
    create_environment_file(connection_string)
    
    # Setup database tables
    if not setup_database_tables():
        sys.exit(1)
    
    # Create initial data
    if not create_initial_data():
        sys.exit(1)
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the .env.example file")
    print("2. Update the SECRET_KEY with a secure value")
    print("3. Deploy to Render using the deployment guide")
    print("4. Set the environment variables in Render dashboard")
    print("\n🔗 Your API will be available at: https://your-app-name.onrender.com")
    print("📚 API Documentation: https://your-app-name.onrender.com/docs")
    print("🏥 Health Check: https://your-app-name.onrender.com/health")

if __name__ == "__main__":
    main() 