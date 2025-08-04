#!/usr/bin/env python3
"""
Test backend health and authentication
"""

import requests
import time

# Backend URL
BASE_URL = "https://garments-pos-backend-92s1.onrender.com"

def test_health():
    """Test backend health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Backend Status: {data['status']}")
            print(f"Database: {data['database']}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_login():
    """Test login"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print(f"Token: {token[:20]}...")
            return token
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_invoices(token):
    """Test invoices endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/invoices/", headers=headers, timeout=30)
        print(f"Invoices: {response.status_code}")
        if response.status_code == 200:
            invoices = response.json()
            print(f"Found {len(invoices)} invoices")
            return True
        else:
            print(f"Invoices failed: {response.text}")
            return False
    except Exception as e:
        print(f"Invoices error: {e}")
        return False

def main():
    print("=== Testing Backend Health ===")
    
    # Test health
    if not test_health():
        print("❌ Backend health check failed")
        return
    
    print("✅ Backend is healthy")
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed")
        return
    
    print("✅ Login successful")
    
    # Test invoices
    if test_invoices(token):
        print("✅ Invoices endpoint working")
    else:
        print("❌ Invoices endpoint failed")

if __name__ == "__main__":
    main() 