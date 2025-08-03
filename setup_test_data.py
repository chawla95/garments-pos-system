#!/usr/bin/env python3
"""
Script to set up complete test data for ML demonstration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
import models
from datetime import datetime, timedelta
import random

def setup_test_data():
    """Set up complete test data for ML demonstration"""
    db = next(get_db())
    
    print("🔧 Setting up complete test data...")
    
    # Create dealers
    dealers = []
    dealer_names = ["Fashion House Ltd", "Trendy Garments", "Style Mart"]
    for i, name in enumerate(dealer_names):
        dealer = models.Dealer(
            name=name,
            pan=f"PAN{i+1}23456789",
            gst=f"GST{i+1}23456789012",
            address=f"Address {i+1}, City {i+1}"
        )
        db.add(dealer)
        dealers.append(dealer)
    
    db.commit()
    print("✅ Created 3 dealers")
    
    # Create brands
    brands = []
    brand_names = ["Nike", "Adidas", "Puma", "Reebok", "Under Armour"]
    for i, name in enumerate(brand_names):
        brand = models.Brand(name=name)
        db.add(brand)
        brands.append(brand)
    
    db.commit()
    print("✅ Created 5 brands")
    
    # Link dealers to brands
    for i, brand in enumerate(brands):
        dealer = dealers[i % len(dealers)]
        dealer_brand = models.DealerBrand(
            dealer_id=dealer.id,
            brand_id=brand.id
        )
        db.add(dealer_brand)
    
    db.commit()
    print("✅ Linked dealers to brands")
    
    # Create products
    products = []
    product_types = ["T-Shirt", "Jeans", "Shirt", "Hoodie", "Sweater"]
    for i, brand in enumerate(brands):
        for j, product_type in enumerate(product_types):
            product = models.Product(
                name=f"{brand.name}-{product_type}",
                brand_id=brand.id,
                type=product_type,
                size_type="ALPHA",
                gst_rate=12.0
            )
            db.add(product)
            products.append(product)
    
    db.commit()
    print("✅ Created 25 products")
    
    # Create inventory items
    for i, product in enumerate(products):
        for j in range(10):  # 10 inventory items per product
            inventory_item = models.InventoryItem(
                product_id=product.id,
                barcode=f"INV{i}{j:02d}",
                design_number=f"DES{i}{j:02d}",
                size=random.choice(["S", "M", "L", "XL"]),
                color=random.choice(["Blue", "Red", "Black", "White", "Green"]),
                cost_price=100.0 + (i * 5) + (j * 2),
                mrp=200.0 + (i * 10) + (j * 5),
                quantity=1
            )
            db.add(inventory_item)
    
    db.commit()
    print("✅ Created 250 inventory items")
    
    # Create test sales data
    base_date = datetime.now() - timedelta(days=90)
    
    for i, product in enumerate(products):
        # Create different sales patterns
        if i < 5:  # High demand products
            sales_pattern = [2, 3, 1, 4, 2, 3, 1, 2, 3, 4, 2, 1, 3, 2, 4, 1, 2, 3, 4, 2, 1, 3, 2, 4, 1, 2, 3, 4, 2, 1]
        elif i < 10:  # Slow moving products
            sales_pattern = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        else:  # Normal products
            sales_pattern = [1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0]
        
        # Create invoices for the past 30 days
        for day in range(30):
            if sales_pattern[day] > 0:
                # Create invoice
                invoice = models.Invoice(
                    invoice_number=f"TEST-INV-{i}-{day}",
                    customer_name=f"Test Customer {day}",
                    customer_phone="+91 98765 43210",
                    customer_email=f"test{day}@example.com",
                    total_mrp=sales_pattern[day] * 200.0,
                    total_discount=0,
                    total_final_price=sales_pattern[day] * 200.0,
                    total_base_amount=sales_pattern[day] * 178.57,
                    total_gst_amount=sales_pattern[day] * 21.43,
                    total_cgst_amount=sales_pattern[day] * 10.71,
                    total_sgst_amount=sales_pattern[day] * 10.71,
                    payment_method="CASH",
                    created_at=base_date + timedelta(days=day)
                )
                db.add(invoice)
                db.flush()
                
                # Create invoice item
                inventory_item = db.query(models.InventoryItem).filter(
                    models.InventoryItem.product_id == product.id
                ).first()
                
                if inventory_item:
                    invoice_item = models.InvoiceItem(
                        invoice_id=invoice.id,
                        inventory_item_id=inventory_item.id,
                        barcode=inventory_item.barcode,
                        product_name=product.name,
                        design_number=inventory_item.design_number,
                        size=inventory_item.size,
                        color=inventory_item.color,
                        unit_price=200.0,
                        quantity=sales_pattern[day],
                        total_price=sales_pattern[day] * 200.0,
                        discount_amount=0,
                        final_price=sales_pattern[day] * 200.0,
                        base_price=sales_pattern[day] * 178.57,
                        gst_amount=sales_pattern[day] * 21.43,
                        cgst_amount=sales_pattern[day] * 10.71,
                        sgst_amount=sales_pattern[day] * 10.71,
                        gst_rate=12.0
                    )
                    db.add(invoice_item)
                    
                    # Update inventory
                    inventory_item.quantity = max(0, inventory_item.quantity - sales_pattern[day])
    
    db.commit()
    print("✅ Created test sales data")
    print("\n📊 Test Data Summary:")
    print("   - 3 Dealers")
    print("   - 5 Brands")
    print("   - 25 Products")
    print("   - 250 Inventory Items")
    print("   - 30 days of sales data")
    print("\n🤖 ML features are now ready to test!")
    print("   - High demand products (first 5)")
    print("   - Slow moving products (next 5)")
    print("   - Normal demand products (remaining)")

if __name__ == "__main__":
    setup_test_data() 