#!/usr/bin/env python3
"""
Simple Admin User Creation for Garments POS System
"""

import os
import sys

def create_admin_user():
    """Create admin user"""
    try:
        from database import SessionLocal
        from models import User, UserRole
        import auth
        
        db = SessionLocal()
        
        # Create admin user directly without checking
        admin_user = User(
            username="admin",
            email="admin@garments-pos.com",
            hashed_password=auth.get_password_hash("admin123"),
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