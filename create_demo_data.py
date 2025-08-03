#!/usr/bin/env python3
"""
Demo Data Creator for Garments POS System
Creates sample users, products, brands, dealers, and transactions
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, engine
import models
from models import User, UserRole, Product, Brand, Dealer, InventoryItem, Invoice, InvoiceItem
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def create_demo_users():
    """Create demo users with different roles"""
    logger.info("Creating demo users...")
    
    demo_users = [
        {
            "username": "admin",
            "email": "admin@garments-pos.com",
            "password": "admin123",
            "role": UserRole.ADMIN,
            "is_active": True
        },
        {
            "username": "manager",
            "email": "manager@garments-pos.com", 
            "password": "manager123",
            "role": UserRole.MANAGER,
            "is_active": True
        },
        {
            "username": "cashier1",
            "email": "cashier1@garments-pos.com",
            "password": "cashier123",
            "role": UserRole.CASHIER,
            "is_active": True
        },
        {
            "username": "cashier2", 
            "email": "cashier2@garments-pos.com",
            "password": "cashier123",
            "role": UserRole.CASHIER,
            "is_active": True
        },
        {
            "username": "demo",
            "email": "demo@garments-pos.com",
            "password": "demo123",
            "role": UserRole.CASHIER,
            "is_active": True
        }
    ]
    
    db = next(get_db())
    
    for user_data in demo_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            logger.info(f"User {user_data['username']} already exists, skipping...")
            continue
            
        # Create new user
        hashed_password = hash_password(user_data["password"])
        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        
        db.add(new_user)
        logger.info(f"Created user: {user_data['username']} ({user_data['role']})")
    
    db.commit()
    logger.info("✅ Demo users created successfully!")

def create_demo_brands():
    """Create demo brands"""
    logger.info("Creating demo brands...")
    
    demo_brands = [
        {"name": "Nike"},
        {"name": "Adidas"},
        {"name": "Puma"},
        {"name": "Levi's"},
        {"name": "Zara"},
        {"name": "H&M"},
        {"name": "Uniqlo"},
        {"name": "Gap"}
    ]
    
    db = next(get_db())
    
    for brand_data in demo_brands:
        existing_brand = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
        if existing_brand:
            logger.info(f"Brand {brand_data['name']} already exists, skipping...")
            continue
            
        new_brand = Brand(**brand_data)
        db.add(new_brand)
        logger.info(f"Created brand: {brand_data['name']}")
    
    db.commit()
    logger.info("✅ Demo brands created successfully!")

def create_demo_dealers():
    """Create demo dealers"""
    logger.info("Creating demo dealers...")
    
    demo_dealers = [
        {"name": "Fashion Wholesale Co.", "pan": "ABCDE1234F", "gst": "27ABCDE1234F1Z5", "address": "Mumbai, Maharashtra"},
        {"name": "Textile Traders Ltd.", "pan": "BCDEF2345G", "gst": "07BCDEF2345G1Z6", "address": "Delhi, NCR"},
        {"name": "Garment Suppliers", "pan": "CDEFG3456H", "gst": "29CDEFG3456H1Z7", "address": "Bangalore, Karnataka"},
        {"name": "Premium Clothing", "pan": "DEFGH4567I", "gst": "33DEFGH4567I1Z8", "address": "Chennai, Tamil Nadu"},
        {"name": "Style Merchants", "pan": "EFGHI5678J", "gst": "19EFGHI5678J1Z9", "address": "Kolkata, West Bengal"}
    ]
    
    db = next(get_db())
    
    for dealer_data in demo_dealers:
        existing_dealer = db.query(Dealer).filter(Dealer.name == dealer_data["name"]).first()
        if existing_dealer:
            logger.info(f"Dealer {dealer_data['name']} already exists, skipping...")
            continue
            
        new_dealer = Dealer(**dealer_data)
        db.add(new_dealer)
        logger.info(f"Created dealer: {dealer_data['name']}")
    
    db.commit()
    logger.info("✅ Demo dealers created successfully!")

def create_demo_products():
    """Create demo products"""
    logger.info("Creating demo products...")
    
    # Get brands for reference
    db = next(get_db())
    brands = db.query(Brand).all()
    
    if not brands:
        logger.error("No brands found! Please create brands first.")
        return
    
    demo_products = [
        {
            "name": "Nike Air Max 270",
            "brand_id": brands[0].id,  # Nike
            "type": "Footwear",
            "size_type": "NUMERIC"
        },
        {
            "name": "Adidas Ultraboost 21",
            "brand_id": brands[1].id,  # Adidas
            "type": "Footwear",
            "size_type": "NUMERIC"
        },
        {
            "name": "Levi's 501 Original Jeans",
            "brand_id": brands[3].id,  # Levi's
            "type": "Bottoms",
            "size_type": "ALPHA"
        },
        {
            "name": "Zara Cotton T-Shirt",
            "brand_id": brands[4].id,  # Zara
            "type": "Tops",
            "size_type": "ALPHA"
        },
        {
            "name": "H&M Slim Fit Shirt",
            "brand_id": brands[5].id,  # H&M
            "type": "Tops",
            "size_type": "ALPHA"
        },
        {
            "name": "Uniqlo Hoodie",
            "brand_id": brands[6].id,  # Uniqlo
            "type": "Outerwear",
            "size_type": "ALPHA"
        },
        {
            "name": "Gap Denim Jacket",
            "brand_id": brands[7].id,  # Gap
            "type": "Outerwear",
            "size_type": "ALPHA"
        },
        {
            "name": "Puma RS-X Sneakers",
            "brand_id": brands[2].id,  # Puma
            "type": "Footwear",
            "size_type": "NUMERIC"
        }
    ]
    
    for product_data in demo_products:
        existing_product = db.query(Product).filter(
            Product.name == product_data["name"],
            Product.brand_id == product_data["brand_id"]
        ).first()
        if existing_product:
            logger.info(f"Product {product_data['name']} already exists, skipping...")
            continue
            
        new_product = Product(**product_data)
        db.add(new_product)
        logger.info(f"Created product: {product_data['name']}")
    
    db.commit()
    logger.info("✅ Demo products created successfully!")

def create_demo_inventory():
    """Create demo inventory items"""
    logger.info("Creating demo inventory...")
    
    db = next(get_db())
    products = db.query(Product).all()
    
    if not products:
        logger.error("No products found! Please create products first.")
        return
    
    # Sample data for inventory items
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    shoe_sizes = ["6", "7", "8", "9", "10", "11", "12"]
    colors = ["Black", "White", "Blue", "Red", "Green", "Gray", "Navy"]
    
    # Create inventory for each product
    for product in products:
        # Determine sizes based on product type
        if product.type == "Footwear":
            available_sizes = shoe_sizes
        else:
            available_sizes = sizes
        
        # Create multiple inventory items for each product (different sizes/colors)
        for size in available_sizes[:3]:  # Create 3 sizes per product
            for color in colors[:2]:  # Create 2 colors per size
                # Generate unique barcode
                barcode = f"{product.id:03d}{ord(size[0])}{ord(color[0])}{random.randint(1000, 9999)}"
                
                # Check if inventory already exists
                existing_inventory = db.query(InventoryItem).filter(
                    InventoryItem.product_id == product.id,
                    InventoryItem.size == size,
                    InventoryItem.color == color
                ).first()
                
                if existing_inventory:
                    logger.info(f"Inventory for {product.name} ({size}, {color}) already exists, skipping...")
                    continue
                
                # Create new inventory item
                inventory_item = InventoryItem(
                    product_id=product.id,
                    barcode=barcode,
                    design_number=f"DES-{product.id:03d}-{size}-{color[:3].upper()}",
                    size=size,
                    color=color,
                    cost_price=float(random.randint(500, 3000)),
                    mrp=float(random.randint(800, 5000)),
                    quantity=1  # Each inventory item represents 1 unit
                )
                db.add(inventory_item)
                logger.info(f"Created inventory for {product.name}: {size}, {color} (Barcode: {barcode})")
    
    db.commit()
    logger.info("✅ Demo inventory created successfully!")

def create_demo_sales():
    """Create demo sales transactions"""
    logger.info("Creating demo sales...")
    
    db = next(get_db())
    inventory_items = db.query(InventoryItem).all()
    users = db.query(User).filter(User.role == UserRole.CASHIER).all()
    
    if not inventory_items:
        logger.error("No inventory items found!")
        return
    
    if not users:
        logger.error("No cashier users found!")
        return
    
    # Create sample sales for the last 30 days
    for day in range(30):
        sale_date = datetime.now() - timedelta(days=day)
        
        # Create 2-5 sales per day
        for sale_num in range(random.randint(2, 5)):
            # Create invoice
            invoice = Invoice(
                invoice_number=f"INV-{sale_date.strftime('%Y%m%d')}-{sale_num:03d}",
                customer_name=f"Customer {day}-{sale_num}",
                customer_phone=f"+91-98765{random.randint(10000, 99999)}",
                customer_email=f"customer{day}{sale_num}@example.com",
                total_mrp=0.0,
                total_discount=0.0,
                total_final_price=0.0,
                total_base_amount=0.0,
                total_gst_amount=0.0,
                total_cgst_amount=0.0,
                total_sgst_amount=0.0,
                payment_method=random.choice(["CASH", "CARD", "UPI"]),
                created_at=sale_date
            )
            db.add(invoice)
            db.flush()  # Get the invoice ID
            
            # Add 1-3 items to the invoice
            total_mrp = 0.0
            total_final_price = 0.0
            total_base_amount = 0.0
            total_gst_amount = 0.0
            total_cgst_amount = 0.0
            total_sgst_amount = 0.0
            
            for item_num in range(random.randint(1, 3)):
                inventory_item = random.choice(inventory_items)
                quantity = random.randint(1, 2)
                unit_price = inventory_item.mrp
                item_total = unit_price * quantity
                discount_amount = item_total * random.uniform(0, 0.2)  # 0-20% discount
                final_price = item_total - discount_amount
                
                # Calculate GST (assuming 12% GST rate)
                gst_rate = 12.0
                base_amount = final_price / (1 + gst_rate/100)
                gst_amount = final_price - base_amount
                cgst_amount = gst_amount / 2
                sgst_amount = gst_amount / 2
                
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    inventory_item_id=inventory_item.id,
                    barcode=inventory_item.barcode,
                    product_name=f"{inventory_item.product.name} - {inventory_item.size}",
                    design_number=inventory_item.design_number,
                    size=inventory_item.size,
                    color=inventory_item.color,
                    unit_price=unit_price,
                    quantity=quantity,
                    total_price=item_total,
                    discount_amount=discount_amount,
                    final_price=final_price,
                    base_price=base_amount,
                    gst_amount=gst_amount,
                    cgst_amount=cgst_amount,
                    sgst_amount=sgst_amount,
                    gst_rate=gst_rate
                )
                db.add(invoice_item)
                
                # Update totals
                total_mrp += item_total
                total_final_price += final_price
                total_base_amount += base_amount
                total_gst_amount += gst_amount
                total_cgst_amount += cgst_amount
                total_sgst_amount += sgst_amount
                
                # Update inventory quantity
                inventory_item.quantity = max(0, inventory_item.quantity - quantity)
            
            # Update invoice totals
            invoice.total_mrp = total_mrp
            invoice.total_discount = total_mrp - total_final_price
            invoice.total_final_price = total_final_price
            invoice.total_base_amount = total_base_amount
            invoice.total_gst_amount = total_gst_amount
            invoice.total_cgst_amount = total_cgst_amount
            invoice.total_sgst_amount = total_sgst_amount
            
            logger.info(f"Created sale: Invoice #{invoice.invoice_number} - ₹{total_final_price:.2f} on {sale_date.strftime('%Y-%m-%d')}")
    
    db.commit()
    logger.info("✅ Demo sales created successfully!")

def main():
    """Main function to create all demo data"""
    logger.info("🚀 Starting demo data creation...")
    
    try:
        # Create all demo data
        create_demo_users()
        create_demo_brands()
        create_demo_dealers()
        create_demo_products()
        create_demo_inventory()
        create_demo_sales()
        
        logger.info("🎉 All demo data created successfully!")
        logger.info("\n📋 Demo Login Credentials:")
        logger.info("👤 admin / admin123 (Admin)")
        logger.info("👤 manager / manager123 (Manager)")
        logger.info("👤 cashier1 / cashier123 (Cashier)")
        logger.info("👤 cashier2 / cashier123 (Cashier)")
        logger.info("👤 demo / demo123 (Cashier)")
        
    except Exception as e:
        logger.error(f"❌ Error creating demo data: {e}")
        raise

if __name__ == "__main__":
    main() 