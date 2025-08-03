#!/usr/bin/env python3
"""
Supabase Setup Helper Script
"""

import os
import sys
import requests
from urllib.parse import urlparse

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🚀 SUPABASE SETUP HELPER")
    print("=" * 60)
    print()

def get_supabase_url():
    """Get Supabase URL from user"""
    print("📋 STEP 1: Get your Supabase connection string")
    print("- Go to your Supabase project dashboard")
    print("- Navigate to Settings → Database")
    print("- Copy the 'URI' connection string")
    print()
    
    while True:
        url = input("🔗 Paste your Supabase connection string: ").strip()
        
        if not url:
            print("❌ Please enter a valid connection string")
            continue
            
        if not url.startswith("postgresql://"):
            print("❌ Connection string should start with 'postgresql://'")
            continue
            
        # Test the URL format
        try:
            parsed = urlparse(url)
            if parsed.scheme == "postgresql" and parsed.hostname and parsed.username:
                print("✅ Valid connection string format")
                return url
            else:
                print("❌ Invalid connection string format")
        except Exception:
            print("❌ Invalid URL format")
            continue

def test_database_connection(url):
    """Test the database connection"""
    print("\n🔧 STEP 2: Testing database connection...")
    
    try:
        # Set the DATABASE_URL environment variable
        os.environ["DATABASE_URL"] = url
        
        # Import and test database connection
        from database import engine
        from models import Base
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful!")
            
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def setup_initial_data():
    """Set up initial data"""
    print("\n📊 STEP 3: Setting up initial data...")
    
    try:
        from setup_database import setup_database
        setup_database()
        print("✅ Initial data setup complete!")
        return True
    except Exception as e:
        print(f"❌ Data setup failed: {str(e)}")
        return False

def generate_env_file(url):
    """Generate environment file for deployment"""
    print("\n📝 STEP 4: Generating environment variables...")
    
    env_content = f"""# Supabase Database Configuration
DATABASE_URL={url}

# Security Configuration
SECRET_KEY=your-super-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
LOG_LEVEL=info
ENVIRONMENT=production
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env.example file")
    print("📋 Copy these variables to your Render environment:")
    print()
    print("DATABASE_URL=" + url)
    print("SECRET_KEY=your-super-secret-key-here-change-this-in-production")
    print("ACCESS_TOKEN_EXPIRE_MINUTES=30")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Get Supabase URL
    url = get_supabase_url()
    
    # Test connection
    if not test_database_connection(url):
        print("\n❌ Setup failed. Please check your connection string.")
        return
    
    # Setup initial data
    if not setup_initial_data():
        print("\n❌ Data setup failed.")
        return
    
    # Generate environment file
    generate_env_file(url)
    
    print("\n🎉 SUPABASE SETUP COMPLETE!")
    print("=" * 60)
    print("Next steps:")
    print("1. Update your Render environment variables")
    print("2. Redeploy your backend")
    print("3. Test the login with admin/admin123")
    print("=" * 60)

if __name__ == "__main__":
    main() 