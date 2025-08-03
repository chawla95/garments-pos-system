#!/usr/bin/env python3
"""
Database setup script for external PostgreSQL database
"""

import os
import sys
from sqlalchemy import create_engine, text
from database import SQLALCHEMY_DATABASE_URL, engine
from models import Base
import auth
import models

def setup_database():
    """Set up the database tables and initial data"""
    print("🔧 Setting up external database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    # Create initial users
    create_initial_users()
    
    # Create test data
    create_test_data()
    
    print("🎉 Database setup complete!")

def create_initial_users():
    """Create initial admin users"""
    from sqlalchemy.orm import Session
    from database import engine
    
    db = Session(engine)
    try:
        # Check if users already exist
        existing_users = db.query(models.User).count()
        if existing_users > 0:
            print(f"ℹ️ {existing_users} users already exist, skipping user creation")
            return
        
        # Create default users
        default_users = [
            {
                "username": "admin",
                "email": "admin@pos.com",
                "password": "admin123",
                "role": models.UserRole.ADMIN,
                "is_active": True
            },
            {
                "username": "cashier",
                "email": "cashier@pos.com", 
                "password": "cashier123",
                "role": models.UserRole.CASHIER,
                "is_active": True
            },
            {
                "username": "inventory",
                "email": "inventory@pos.com",
                "password": "inventory123", 
                "role": models.UserRole.INVENTORY_MANAGER,
                "is_active": True
            }
        ]
        
        for user_data in default_users:
            # Check if user already exists
            existing_user = db.query(models.User).filter(models.User.username == user_data["username"]).first()
            if not existing_user:
                # Create new user
                hashed_password = auth.get_password_hash(user_data["password"])
                new_user = models.User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    role=user_data["role"],
                    is_active=user_data["is_active"]
                )
                db.add(new_user)
                print(f"✅ Created user: {user_data['username']}")
            else:
                print(f"ℹ️ User already exists: {user_data['username']}")
        
        db.commit()
        print("✅ Initial users created successfully")
        
    except Exception as e:
        print(f"❌ Error creating users: {str(e)}")
        db.rollback()
    finally:
        db.close()

def create_test_data():
    """Create test data for the POS system"""
    from sqlalchemy.orm import Session
    from database import engine
    from datetime import datetime, timedelta
    import random
    
    db = Session(engine)
    try:
        # Create test dealers
        dealers = [
            {"name": "Fashion Forward Ltd", "pan": "ABCDE1234F", "gst": "27ABCDE1234F1Z5", "address": "Mumbai, Maharashtra"},
            {"name": "Trendy Garments Co", "pan": "BCDEF2345G", "gst": "27BCDEF2345G2Z6", "address": "Delhi, NCR"},
            {"name": "Style Solutions", "pan": "CDEFG3456H", "gst": "27CDEFG3456H3Z7", "address": "Bangalore, Karnataka"}
        ]
        
        for dealer_data in dealers:
            existing_dealer = db.query(models.Dealer).filter(models.Dealer.name == dealer_data["name"]).first()
            if not existing_dealer:
                dealer = models.Dealer(**dealer_data)
                db.add(dealer)
                print(f"✅ Created dealer: {dealer_data['name']}")
        
        # Create test brands
        brands = [
            {"name": "Nike", "description": "Sports and casual wear"},
            {"name": "Adidas", "description": "Athletic footwear and apparel"},
            {"name": "Puma", "description": "Sports lifestyle products"},
            {"name": "Levi's", "description": "Denim and casual wear"},
            {"name": "Zara", "description": "Fast fashion clothing"}
        ]
        
        for brand_data in brands:
            existing_brand = db.query(models.Brand).filter(models.Brand.name == brand_data["name"]).first()
            if not existing_brand:
                brand = models.Brand(**brand_data)
                db.add(brand)
                print(f"✅ Created brand: {brand_data['name']}")
        
        db.commit()
        print("✅ Test data created successfully")
        
    except Exception as e:
        print(f"❌ Error creating test data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database() 