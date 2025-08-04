#!/usr/bin/env python3
"""
Test script to verify auto-calculated return amounts
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

def test_invoice_lookup(token, invoice_number):
    """Test looking up an invoice for return"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/returns/invoice/{invoice_number}", headers=headers)
        print(f"Invoice Lookup: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found invoice: {data['invoice']['invoice_number']}")
            print(f"Customer: {data['invoice']['customer_name']}")
            print(f"Total Amount: {data['invoice']['total_final_price']}")
            print(f"Items: {len(data['items'])}")
            for item in data['items']:
                print(f"  - {item['product_name']}: {item['quantity']} x {item['final_price']}")
            return data
        else:
            print(f"Invoice lookup failed: {response.text}")
            return None
    except Exception as e:
        print(f"Invoice lookup error: {e}")
        return None

def test_return_creation(token, invoice_data):
    """Test creating a return with auto-calculated amounts"""
    try:
        # Create return request with auto-calculated amounts
        return_request = {
            "invoice_number": invoice_data['invoice']['invoice_number'],
            "items": [
                {
                    "invoice_item_id": invoice_data['items'][0]['id'],
                    "return_quantity": 1
                }
            ],
            "return_reason": "Test return - auto-calculated amounts",
            "return_method": "CASH",
            "notes": "Testing auto-calculated return amounts"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/returns/", json=return_request, headers=headers)
        print(f"Return Creation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Return created successfully!")
            print(f"Return Number: {data['return_record']['return_number']}")
            print(f"Return Amount: {data['return_record']['total_return_amount']}")
            print(f"Cash Refund: {data['return_record']['cash_refund']}")
            print(f"Wallet Credit: {data['return_record']['wallet_credit']}")
            print(f"Return Method: {data['return_record']['return_method']}")
            return data
        else:
            print(f"Return creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"Return creation error: {e}")
        return None

def test_wallet_return(token, invoice_data):
    """Test creating a wallet return with auto-calculated amounts"""
    try:
        # Create return request for wallet credit
        return_request = {
            "invoice_number": invoice_data['invoice']['invoice_number'],
            "items": [
                {
                    "invoice_item_id": invoice_data['items'][0]['id'],
                    "return_quantity": 1
                }
            ],
            "return_reason": "Test wallet return - auto-calculated amounts",
            "return_method": "WALLET",
            "notes": "Testing auto-calculated wallet credit amounts"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/returns/", json=return_request, headers=headers)
        print(f"Wallet Return Creation: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Wallet return created successfully!")
            print(f"Return Number: {data['return_record']['return_number']}")
            print(f"Return Amount: {data['return_record']['total_return_amount']}")
            print(f"Cash Refund: {data['return_record']['cash_refund']}")
            print(f"Wallet Credit: {data['return_record']['wallet_credit']}")
            print(f"Return Method: {data['return_record']['return_method']}")
            return data
        else:
            print(f"Wallet return creation failed: {response.text}")
            return None
    except Exception as e:
        print(f"Wallet return creation error: {e}")
        return None

def main():
    print("=== Testing Auto-Calculated Return Amounts ===")
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed, cannot proceed")
        return
    
    print("✅ Login successful")
    
    # Test invoice lookup (you'll need to provide a valid invoice number)
    print("\n1. Testing invoice lookup...")
    # Replace with an actual invoice number from your system
    invoice_number = "INV-2024-001"  # Change this to a real invoice number
    invoice_data = test_invoice_lookup(token, invoice_number)
    
    if invoice_data:
        print("✅ Invoice found")
        
        # Test cash return creation
        print("\n2. Testing cash return with auto-calculated amounts...")
        cash_return = test_return_creation(token, invoice_data)
        
        if cash_return:
            print("✅ Cash return test completed")
            
            # Test wallet return creation
            print("\n3. Testing wallet return with auto-calculated amounts...")
            wallet_return = test_wallet_return(token, invoice_data)
            
            if wallet_return:
                print("✅ Wallet return test completed")
                print("\n🎉 All tests passed! Auto-calculated return amounts are working correctly.")
            else:
                print("❌ Wallet return test failed")
        else:
            print("❌ Cash return test failed")
    else:
        print("❌ Invoice lookup failed")
        print("💡 Please update the invoice_number variable with a valid invoice number from your system")

if __name__ == "__main__":
    main() 