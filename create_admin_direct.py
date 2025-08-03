#!/usr/bin/env python3
"""
Direct Admin User Creation - Bypasses FastAPI imports
"""

import os
import sys
import hashlib
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_admin_user():
    """Create admin user directly"""
    try:
        from database import SessionLocal
        from models import User, UserRole
        
        db = SessionLocal()
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@garments-pos.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created successfully")
        print("📋 Login credentials: admin / admin123")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Creating admin user...")
    
    if create_admin_user():
        print("🎉 Admin user setup completed!")
        print("\n📋 Default credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  Remember to change the password after first login!")
    else:
        print("❌ Failed to create admin user")
        sys.exit(1)

if __name__ == "__main__":
    main() 