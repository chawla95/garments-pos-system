#!/usr/bin/env python3
"""
Test script to debug the products endpoint 500 error
"""

import requests
import json

# Backend URL
BASE_URL = "https://garments-pos-backend-92s1.onrender.com"

def test_health():
    """Test if backend is healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_login():
    """Test login to get a token"""
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Token: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_products_with_auth(token):
    """Test products endpoint with authentication"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/products", headers=headers)
        print(f"Products with auth: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Products found: {len(data)}")
            return True
        else:
            print(f"Products failed: {response.text}")
            return False
    except Exception as e:
        print(f"Products test failed: {e}")
        return False

def test_products_without_auth():
    """Test products endpoint without authentication"""
    try:
        response = requests.get(f"{BASE_URL}/products")
        print(f"Products without auth: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code
    except Exception as e:
        print(f"Products without auth failed: {e}")
        return None

def test_brands_with_auth(token):
    """Test brands endpoint with authentication"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/brands", headers=headers)
        print(f"Brands with auth: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Brands found: {len(data)}")
            return True
        else:
            print(f"Brands failed: {response.text}")
            return False
    except Exception as e:
        print(f"Brands test failed: {e}")
        return False

def main():
    print("=== Testing Backend Endpoints ===")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    if not test_health():
        print("❌ Backend is not healthy")
        return
    
    # Test 2: Login
    print("\n2. Testing login...")
    token = test_login()
    if not token:
        print("❌ Login failed")
        return
    
    # Test 3: Products without auth
    print("\n3. Testing products without authentication...")
    test_products_without_auth()
    
    # Test 4: Products with auth
    print("\n4. Testing products with authentication...")
    test_products_with_auth(token)
    
    # Test 5: Brands with auth (to see if it's a general issue)
    print("\n5. Testing brands with authentication...")
    test_brands_with_auth(token)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 