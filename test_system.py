#!/usr/bin/env python3
"""
Test script for Garments POS System
Run this after starting the server to verify all functionality works correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_system():
    print("🧪 Testing Garments POS System...")
    print("=" * 50)
    
    # Test 1: Create Dealer
    print("\n1. Creating Dealer...")
    dealer_data = {
        "name": "Fashion Supplier Ltd",
        "gstin": "GST123456789",
        "contact": "+91-9876543210"
    }
    response = requests.post(f"{BASE_URL}/dealers/", json=dealer_data)
    if response.status_code == 201:
        dealer = response.json()
        print(f"✅ Dealer created: {dealer['name']} (ID: {dealer['id']})")
        dealer_id = dealer['id']
    else:
        print(f"❌ Failed to create dealer: {response.text}")
        return
    
    # Test 2: Create Brand
    print("\n2. Creating Brand...")
    brand_data = {"name": "Nike"}
    response = requests.post(f"{BASE_URL}/brands/", json=brand_data)
    if response.status_code == 201:
        brand = response.json()
        print(f"✅ Brand created: {brand['name']} (ID: {brand['id']})")
        brand_id = brand['id']
    else:
        print(f"❌ Failed to create brand: {response.text}")
        return
    
    # Test 3: Create Product
    print("\n3. Creating Product...")
    product_data = {
        "name": "Nike T-Shirt",
        "brand_id": brand_id,
        "design_number": "NK001",
        "size": "M",
        "color": "Blue",
        "type": "T-Shirt",
        "cost_price": 500.0,
        "mrp": 1200.0
    }
    response = requests.post(f"{BASE_URL}/products/", json=product_data)
    if response.status_code == 201:
        product = response.json()
        print(f"✅ Product created: {product['name']} (ID: {product['id']})")
        product_id = product['id']
    else:
        print(f"❌ Failed to create product: {response.text}")
        return
    
    # Test 4: Add First Inventory Item
    print("\n4. Adding First Inventory Item...")
    inventory_data = {
        "product_id": product_id,
        "barcode": "1234567890123",
        "quantity": 10
    }
    response = requests.post(f"{BASE_URL}/inventory/", json=inventory_data)
    if response.status_code == 201:
        inventory = response.json()
        print(f"✅ Inventory item created: Barcode {inventory['barcode']}, Quantity: {inventory['quantity']}")
    else:
        print(f"❌ Failed to create inventory item: {response.text}")
        return
    
    # Test 5: Add Second Inventory Item (same product, different barcode)
    print("\n5. Adding Second Inventory Item (same product, different barcode)...")
    inventory_data2 = {
        "product_id": product_id,
        "barcode": "1234567890124",
        "quantity": 5
    }
    response = requests.post(f"{BASE_URL}/inventory/", json=inventory_data2)
    if response.status_code == 201:
        inventory2 = response.json()
        print(f"✅ Second inventory item created: Barcode {inventory2['barcode']}, Quantity: {inventory2['quantity']}")
    else:
        print(f"❌ Failed to create second inventory item: {response.text}")
        return
    
    # Test 6: View Inventory by Product
    print("\n6. Viewing Inventory by Product...")
    response = requests.get(f"{BASE_URL}/inventory/product/{product_id}")
    if response.status_code == 200:
        inventory_summary = response.json()
        print(f"✅ Product: {inventory_summary['product_name']}")
        print(f"   Brand: {inventory_summary['brand_name']}")
        print(f"   Total Quantity: {inventory_summary['total_quantity']}")
        print(f"   Number of inventory items: {len(inventory_summary['inventory_items'])}")
    else:
        print(f"❌ Failed to get inventory summary: {response.text}")
        return
    
    # Test 7: Subtract Inventory by Barcode
    print("\n7. Subtracting Inventory by Barcode...")
    subtract_data = {
        "barcode": "1234567890123",
        "quantity": 2
    }
    response = requests.put(f"{BASE_URL}/inventory/subtract", json=subtract_data)
    if response.status_code == 200:
        updated_inventory = response.json()
        print(f"✅ Inventory updated: Barcode {updated_inventory['barcode']}, New Quantity: {updated_inventory['quantity']}")
    else:
        print(f"❌ Failed to subtract inventory: {response.text}")
        return
    
    # Test 8: View Updated Inventory by Product
    print("\n8. Viewing Updated Inventory by Product...")
    response = requests.get(f"{BASE_URL}/inventory/product/{product_id}")
    if response.status_code == 200:
        inventory_summary = response.json()
        print(f"✅ Updated Total Quantity: {inventory_summary['total_quantity']}")
    else:
        print(f"❌ Failed to get updated inventory summary: {response.text}")
        return
    
    # Test 9: Test Error Cases
    print("\n9. Testing Error Cases...")
    
    # Try to create duplicate barcode
    print("   Testing duplicate barcode...")
    response = requests.post(f"{BASE_URL}/inventory/", json=inventory_data)
    if response.status_code == 400:
        print("   ✅ Correctly rejected duplicate barcode")
    else:
        print(f"   ❌ Should have rejected duplicate barcode: {response.text}")
    
    # Try to subtract more than available
    print("   Testing insufficient stock...")
    subtract_data = {
        "barcode": "1234567890123",
        "quantity": 20
    }
    response = requests.put(f"{BASE_URL}/inventory/subtract", json=subtract_data)
    if response.status_code == 400:
        print("   ✅ Correctly rejected insufficient stock")
    else:
        print(f"   ❌ Should have rejected insufficient stock: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("📖 Access the API documentation at: http://localhost:8000/docs")
    print("🔗 Test the endpoints manually using the Swagger UI")

if __name__ == "__main__":
    try:
        test_system()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running with:")
        print("   uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 