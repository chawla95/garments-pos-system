#!/usr/bin/env python3
"""
Script to create test sales data for ML demonstration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db
import models
from datetime import datetime, timedelta
import random

def create_test_data():
    """Create test sales data for ML demonstration"""
    db = next(get_db())
    
    # Check if we have products
    products = db.query(models.Product).all()
    if not products:
        print("No products found. Please create some products first.")
        return
    
    print(f"Found {len(products)} products. Creating test sales data...")
    
    # Create test invoices with sales data over the past 90 days
    for i, product in enumerate(products):
        # Create some inventory items for this product
        for j in range(5):  # 5 inventory items per product
            inventory_item = models.InventoryItem(
                product_id=product.id,
                barcode=f"TEST{i}{j}",
                design_number=f"DES{i}{j}",
                size="M",
                color="Blue",
                cost_price=100.0 + (i * 10),
                mrp=200.0 + (i * 20),
                quantity=1
            )
            db.add(inventory_item)
        
        # Create sales data over the past 90 days
        base_date = datetime.now() - timedelta(days=90)
        
        # Create different sales patterns for different products
        if i == 0:  # High demand product
            sales_pattern = [2, 3, 1, 4, 2, 3, 1, 2, 3, 4, 2, 1, 3, 2, 4, 1, 2, 3, 4, 2, 1, 3, 2, 4, 1, 2, 3, 4, 2, 1]
        elif i == 1:  # Slow moving product
            sales_pattern = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        else:  # Normal product
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
                db.flush()  # Get the invoice ID
                
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
    print("✅ Test sales data created successfully!")
    print("📊 Created sales patterns:")
    print("   - Product 1: High demand (frequent sales)")
    print("   - Product 2: Slow moving (occasional sales)")
    print("   - Other products: Normal demand")
    print("\n🤖 You can now test the ML forecasting features!")

if __name__ == "__main__":
    print("🔧 Creating test sales data for ML demonstration...")
    create_test_data() 