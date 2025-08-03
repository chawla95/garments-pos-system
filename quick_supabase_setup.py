#!/usr/bin/env python3
"""
Quick Supabase Setup Script
Usage: python quick_supabase_setup.py "your-connection-string"
"""

import os
import sys
from urllib.parse import urlparse

def setup_supabase(connection_string):
    """Set up Supabase with the provided connection string"""
    print("🚀 Setting up Supabase database...")
    print(f"Connection string: {connection_string[:50]}...")
    
    # Validate connection string
    if not connection_string.startswith("postgresql://"):
        print("❌ Error: Connection string must start with 'postgresql://'")
        return False
    
    try:
        parsed = urlparse(connection_string)
        if not parsed.hostname or not parsed.username:
            print("❌ Error: Invalid connection string format")
            return False
    except Exception:
        print("❌ Error: Invalid URL format")
        return False
    
    # Set environment variable
    os.environ["DATABASE_URL"] = connection_string
    
    try:
        # Test database connection
        print("🔧 Testing database connection...")
        from database import engine
        from models import Base
        
        # Test connection
        with engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Setup initial data
        print("📊 Setting up initial data...")
        from setup_database import setup_database
        setup_database()
        print("✅ Initial data setup complete!")
        
        # Generate environment variables
        print("\n📝 Environment variables for Render:")
        print("=" * 50)
        print(f"DATABASE_URL={connection_string}")
        print("SECRET_KEY=your-super-secret-key-here-change-this-in-production")
        print("ACCESS_TOKEN_EXPIRE_MINUTES=30")
        print("=" * 50)
        
        print("\n🎉 Supabase setup complete!")
        print("Next steps:")
        print("1. Copy the environment variables above")
        print("2. Add them to your Render environment")
        print("3. Redeploy your backend")
        print("4. Test login with admin/admin123")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python quick_supabase_setup.py \"your-connection-string\"")
        print("\nExample:")
        print("python quick_supabase_setup.py \"postgresql://postgres.xxx:password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres\"")
        return
    
    connection_string = sys.argv[1]
    setup_supabase(connection_string)

if __name__ == "__main__":
    main() 