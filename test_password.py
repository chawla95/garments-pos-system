#!/usr/bin/env python3
"""
Test script to check password hashing and verification
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext
import auth

def test_password_hashing():
    """Test password hashing and verification"""
    print("🔧 Testing password hashing...")
    
    # Test password
    test_password = "cashier123"
    
    # Hash the password
    hashed_password = auth.get_password_hash(test_password)
    print(f"Original password: {test_password}")
    print(f"Hashed password: {hashed_password}")
    
    # Verify the password
    is_valid = auth.verify_password(test_password, hashed_password)
    print(f"Password verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test with wrong password
    wrong_password = "wrong123"
    is_wrong_valid = auth.verify_password(wrong_password, hashed_password)
    print(f"Wrong password verification: {'❌ Should be invalid' if not is_wrong_valid else '⚠️  Should be invalid but is valid'}")
    
    return is_valid

def test_specific_passwords():
    """Test the specific passwords we're using"""
    print("\n🔧 Testing specific passwords...")
    
    passwords_to_test = [
        ("cashier", "cashier123"),
        ("inventory", "inventory123"),
        ("admin", "admin123")
    ]
    
    for username, password in passwords_to_test:
        hashed = auth.get_password_hash(password)
        is_valid = auth.verify_password(password, hashed)
        print(f"{username}/{password}: {'✅ Valid' if is_valid else '❌ Invalid'}")

if __name__ == "__main__":
    test_password_hashing()
    test_specific_passwords() 