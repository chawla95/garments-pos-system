#!/usr/bin/env python3
"""
Test Database Connection and Models
"""

import os

def test_database():
    """Test database connection and models"""
    try:
        print("🔍 Testing database connection...")
        from database import engine, SessionLocal
        from models import User, UserRole
        import auth
        
        print("✅ Database imports successful")
        
        # Test session creation
        print("🔍 Testing session creation...")
        db = SessionLocal()
        print("✅ Session created successfully")
        
        # Test simple query
        print("🔍 Testing simple query...")
        result = db.execute("SELECT 1")
        print("✅ Simple query successful")
        
        # Test User model creation
        print("🔍 Testing User model creation...")
        admin_user = User(
            username="admin",
            email="admin@garments-pos.com",
            hashed_password=auth.get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        print("✅ User model creation successful")
        
        # Test adding to database
        print("🔍 Testing database insertion...")
        db.add(admin_user)
        db.commit()
        print("✅ Database insertion successful")
        
        db.close()
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database() 