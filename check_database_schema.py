#!/usr/bin/env python3
"""
Check database schema to identify the validation error
"""

import requests
import json

# Backend URL
BASE_URL = "https://garments-pos-backend-92s1.onrender.com"

def test_database_schema():
    """Test database schema by trying to access different endpoints"""
    
    # First, get a token
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
        
        token = response.json()['access_token']
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("✅ Login successful")
        
        # Test different endpoints to see which ones work
        endpoints = [
            ("/brands", "Brands"),
            ("/dealers", "Dealers"),
            ("/products", "Products"),
            ("/inventory", "Inventory"),
            ("/customers", "Customers"),
            ("/invoices", "Invoices")
        ]
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
                print(f"{name}: {response.status_code}")
                if response.status_code != 200:
                    print(f"  Error: {response.text}")
                else:
                    data = response.json()
                    print(f"  Found {len(data)} items")
            except Exception as e:
                print(f"{name}: Error - {e}")
        
        # Test creating a simple brand to see if that works
        print("\n--- Testing Brand Creation ---")
        brand_data = {
            "name": "Test Brand",
            "description": "Test brand for debugging"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/brands", json=brand_data, headers=headers)
            print(f"Create Brand: {response.status_code}")
            if response.status_code == 201:
                print("✅ Brand creation successful")
                brand_id = response.json()['id']
                
                # Try to create a product
                print("\n--- Testing Product Creation ---")
                product_data = {
                    "brand_id": brand_id,
                    "type": "Test Product",
                    "size_type": "ALPHA",
                    "gst_rate": 12.0
                }
                
                response = requests.post(f"{BASE_URL}/products", json=product_data, headers=headers)
                print(f"Create Product: {response.status_code}")
                if response.status_code == 201:
                    print("✅ Product creation successful")
                    product_id = response.json()['id']
                    
                    # Now try to get products
                    print("\n--- Testing Products Retrieval ---")
                    response = requests.get(f"{BASE_URL}/products", headers=headers)
                    print(f"Get Products: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Products retrieval successful - found {len(data)} products")
                    else:
                        print(f"❌ Products retrieval failed: {response.text}")
                else:
                    print(f"❌ Product creation failed: {response.text}")
            else:
                print(f"❌ Brand creation failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during creation test: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== Database Schema Check ===")
    test_database_schema() 