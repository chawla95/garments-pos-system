#!/usr/bin/env python3
"""
Test script to verify invoice creation and listing
"""

import requests
import json

# Backend URL
BASE_URL = "https://garments-pos-backend-92s1.onrender.com"

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
            return data["access_token"]
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_invoice_creation(token):
    """Test creating an invoice"""
    try:
        checkout_data = {
            "items": [
                {
                    "barcode": "1234567890",
                    "quantity": 1
                }
            ],
            "customer_name": "Test Customer",
            "customer_phone": "9876543210",
            "customer_email": "test@example.com",
            "discount_type": None,
            "discount_value": 0,
            "loyalty_points_redeemed": 0,
            "payment_method": "CASH",
            "notes": "Test invoice"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/checkout/", json=checkout_data, headers=headers)
        print(f"Invoice Creation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Invoice created: {data['invoice']['invoice_number']}")
            return data['invoice']['id']
        else:
            print(f"Invoice creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"Invoice creation error: {e}")
        return None

def test_invoice_listing(token):
    """Test listing invoices"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/invoices/", headers=headers)
        print(f"Invoice Listing: {response.status_code}")
        if response.status_code == 200:
            invoices = response.json()
            print(f"Found {len(invoices)} invoices")
            for invoice in invoices:
                print(f"  - {invoice['invoice_number']}: {invoice['customer_name']} - ₹{invoice['total_final_price']}")
            return invoices
        else:
            print(f"Invoice listing failed: {response.text}")
            return []
    except Exception as e:
        print(f"Invoice listing error: {e}")
        return []

def main():
    print("=== Testing Invoice Creation and Listing ===")
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed, cannot proceed")
        return
    
    print("✅ Login successful")
    
    # Test invoice listing before creation
    print("\n1. Testing invoice listing before creation...")
    invoices_before = test_invoice_listing(token)
    
    # Test invoice creation
    print("\n2. Testing invoice creation...")
    invoice_id = test_invoice_creation(token)
    
    if invoice_id:
        print("✅ Invoice created successfully")
        
        # Test invoice listing after creation
        print("\n3. Testing invoice listing after creation...")
        invoices_after = test_invoice_listing(token)
        
        if len(invoices_after) > len(invoices_before):
            print("✅ Invoice appears in listing")
        else:
            print("❌ Invoice not appearing in listing")
    else:
        print("❌ Invoice creation failed")

if __name__ == "__main__":
    main() 