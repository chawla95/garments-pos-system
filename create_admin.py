#!/usr/bin/env python3
"""
Script to create the initial admin user for the POS system.
Run this script once to set up the admin user.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
import models
import auth
from sqlalchemy.orm import Session

def create_admin_user():
    """Create the initial admin user"""
    db = next(get_db())
    
    # Check if admin user already exists
    admin_user = db.query(models.User).filter(models.User.username == "admin").first()
    if admin_user:
        print("Admin user already exists!")
        return
    
    # Create admin user
    hashed_password = auth.get_password_hash("admin123")
    admin_user = models.User(
        username="admin",
        email="admin@pos.com",
        hashed_password=hashed_password,
        role=models.UserRole.ADMIN,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    print("✅ Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("Role: ADMIN")
    print("\n⚠️  Please change the password after first login!")

def create_sample_users():
    """Create sample users for testing"""
    db = next(get_db())
    
    # Create cashier user
    cashier_user = db.query(models.User).filter(models.User.username == "cashier").first()
    if not cashier_user:
        hashed_password = auth.get_password_hash("cashier123")
        cashier_user = models.User(
            username="cashier",
            email="cashier@pos.com",
            hashed_password=hashed_password,
            role=models.UserRole.CASHIER,
            is_active=True
        )
        db.add(cashier_user)
        print("✅ Cashier user created!")
    
    # Create inventory manager user
    inventory_user = db.query(models.User).filter(models.User.username == "inventory").first()
    if not inventory_user:
        hashed_password = auth.get_password_hash("inventory123")
        inventory_user = models.User(
            username="inventory",
            email="inventory@pos.com",
            hashed_password=hashed_password,
            role=models.UserRole.INVENTORY_MANAGER,
            is_active=True
        )
        db.add(inventory_user)
        print("✅ Inventory Manager user created!")
    
    db.commit()
    print("\n📋 Sample Users Created:")
    print("Cashier - Username: cashier, Password: cashier123")
    print("Inventory Manager - Username: inventory, Password: inventory123")

if __name__ == "__main__":
    print("🔧 Setting up POS System Users...")
    create_admin_user()
    create_sample_users()
    print("\n🎉 User setup complete!") 