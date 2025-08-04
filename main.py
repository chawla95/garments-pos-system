from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from typing import List, Optional
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, database, auth
import uuid
import datetime
from pdf_generator import pdf_generator
from datetime import datetime, timedelta
from ml_forecasting import InventoryOptimizer
from whatsapp_service import whatsapp_service
from rbac_service import rbac_service
from config import settings
from error_handler import setup_error_handlers, health_check as error_health_check, validate_dependencies, validate_database_connection
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Run database migration for description column
try:
    from add_description_column import add_description_column
    add_description_column()
except Exception as e:
    logger.warning(f"Database migration warning: {e}")

# Run database migration for gst_rate column
try:
    from add_gst_rate_column import add_gst_rate_column
    add_gst_rate_column()
except Exception as e:
    logger.warning(f"Database migration warning: {e}")

app = FastAPI(
    title="Garments POS System API",
    description="A comprehensive POS system for garments retail",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:5173",
        "https://garments-pos-frontend.onrender.com",  # Render frontend
        "https://garments-pos-system.vercel.app",      # Vercel frontend
        "https://pos-frontend-d67i3dpx6-abhisheks-projects-f92c4bb9.vercel.app",  # Current Vercel deployment
        "https://pos-frontend-eamd6hk64-abhisheks-projects-f92c4bb9.vercel.app",  # Previous Vercel deployment
        "https://pos-frontend-3clnf3598-abhisheks-projects-f92c4bb9.vercel.app",  # Latest Vercel deployment
        "https://*.vercel.app",  # Allow all Vercel subdomains
        "*"  # Allow all origins in development - remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== HEALTH CHECK ====================
@app.get("/health")
def health_check():
    """Comprehensive health check endpoint with dependency validation"""
    try:
        # Validate dependencies
        validate_dependencies()
        
        # Validate database connection
        validate_database_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "dependencies": "ok",
            "database": "ok"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "error": str(e),
            "type": type(e).__name__
        }

# ==================== FAVICON ENDPOINT ====================
@app.get("/favicon.ico")
def get_favicon():
    """Handle favicon requests to prevent 404 errors"""
    return Response(status_code=204)  # No content response

# ==================== AUTHENTICATION ENDPOINTS ====================
@app.post("/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user (Admin only)"""
    # Check if username already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/auth/login", response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """Login user and return JWT token"""
    user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
    if not user or not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Create access token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    # Convert user to dict for response
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_dict
    }

@app.get("/auth/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current user information"""
    return current_user

@app.get("/auth/users", response_model=List[schemas.User])
def get_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get all users (Admin only)"""
    users = db.query(models.User).all()
    return users

# ==================== ROOT ENDPOINT ====================
@app.get("/")
def read_root():
    return {
        "message": "Garments POS System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# ==================== DEBUG ENDPOINT ====================
@app.post("/debug/create-admin")
def create_admin_debug(db: Session = Depends(database.get_db)):
    """Debug endpoint to create admin user"""
    try:
        # Check if admin user already exists
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if admin_user:
            return {"message": "Admin user already exists", "username": "admin", "password": "admin123"}
        
        # Create admin user
        hashed_password = auth.get_password_hash("admin123")
        admin_user = models.User(
            username="admin",
            email="admin@pos.com",
            hashed_password=hashed_password,
            role=models.UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        return {
            "message": "Admin user created successfully",
            "username": "admin",
            "password": "admin123",
            "role": "ADMIN"
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/users")
def get_users_debug(db: Session = Depends(database.get_db)):
    """Debug endpoint to list all users"""
    try:
        users = db.query(models.User).all()
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
                "hashed_password": user.hashed_password[:20] + "..." if user.hashed_password else None
            })
        return {"users": user_list, "count": len(user_list)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/debug/create-all-users")
def create_all_users_debug(db: Session = Depends(database.get_db)):
    """Debug endpoint to create all test users"""
    try:
        users_created = []
        
        # Create admin user
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            hashed_password = auth.get_password_hash("admin123")
            admin_user = models.User(
                username="admin",
                email="admin@pos.com",
                hashed_password=hashed_password,
                role=models.UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            users_created.append({"username": "admin", "password": "admin123", "role": "ADMIN"})
        
        # Create cashier user
        cashier_user = db.query(models.User).filter(models.User.username == "cashier").first()
        if not cashier_user:
            hashed_password = auth.get_password_hash("cashier123")
            cashier_user = models.User(
                username="cashier",
                email="cashier@pos.com",
                hashed_password=hashed_password,
                role=models.UserRole.CASHIER,
                is_active=True
            )
            db.add(cashier_user)
            users_created.append({"username": "cashier", "password": "cashier123", "role": "CASHIER"})
        
        # Create inventory user
        inventory_user = db.query(models.User).filter(models.User.username == "inventory").first()
        if not inventory_user:
            hashed_password = auth.get_password_hash("inventory123")
            inventory_user = models.User(
                username="inventory",
                email="inventory@pos.com",
                hashed_password=hashed_password,
                role=models.UserRole.INVENTORY_MANAGER,
                is_active=True
            )
            db.add(inventory_user)
            users_created.append({"username": "inventory", "password": "inventory123", "role": "INVENTORY_MANAGER"})
        
        db.commit()
        
        return {
            "message": "Users created successfully",
            "users_created": users_created
        }
    except Exception as e:
        return {"error": str(e)}

# ==================== SIZE SCALE CONSTANTS ====================
SIZE_SCALES = {
    "ALPHA": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"],
    "NUMERIC": ["2", "4", "6", "8", "10", "12", "14", "16", "18", "20", "22", "24", "26", "28", "30", "32", "34", "36", "38", "40", "42", "44", "46", "48", "50"],
    "CUSTOM": []  # Will be filled by user input
}

# ==================== PRODUCT TYPE CONSTANTS ====================
PRODUCT_TYPES = [
    "T-Shirt", "Shirt", "Jeans", "Trousers", "Shorts", "Dress", "Skirt", 
    "Jacket", "Sweater", "Hoodie", "Blazer", "Suit", "Waistcoat", "Kurta",
    "Saree", "Lehenga", "Anarkali", "Palazzo", "Leggings", "Jumpsuit",
    "Blouse", "Top", "Cardigan", "Coat", "Sweatshirt", "Polo", "Tank Top",
    "Crop Top", "Bodycon", "A-Line", "Maxi", "Mini", "Midi", "Pencil",
    "Pleated", "Wrap", "Shift", "Sheath", "Empire", "Boat Neck", "V-Neck",
    "Round Neck", "Collar", "Sleeveless", "Short Sleeve", "Long Sleeve",
    "3/4 Sleeve", "Bell Sleeve", "Puff Sleeve", "Ruffle", "Lace", "Embroidered"
]

def generate_invoice_number():
    """Generate a unique invoice number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"INV-{timestamp}-{random_suffix}"

@app.post("/checkout/", response_model=schemas.CheckoutResponse)
def create_checkout(
    checkout_data: schemas.CheckoutRequest, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Create a new invoice from checkout data with proper Indian retail billing"""
    try:
        # Validate all items exist and have sufficient stock
        items_to_process = []
        total_mrp = 0
        
        for item in checkout_data.items:
            inventory_item = db.query(models.InventoryItem).filter(
                models.InventoryItem.barcode == item.barcode
            ).first()
            
            if not inventory_item:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Inventory item with barcode {item.barcode} not found"
                )
            
            if inventory_item.quantity < item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for barcode {item.barcode}. Available: {inventory_item.quantity}, Requested: {item.quantity}"
                )
            
            # Get product details for invoice
            product = db.query(models.Product).filter(models.Product.id == inventory_item.product_id).first()
            product_name = product.name if product else "Unknown Product"
            gst_rate = product.gst_rate if product else 12.0  # Default 12% GST
            
            # Calculate item totals (MRP is GST-inclusive)
            item_mrp = inventory_item.mrp * item.quantity
            total_mrp += item_mrp
            
            items_to_process.append({
                'inventory_item': inventory_item,
                'quantity': item.quantity,
                'product_name': product_name,
                'item_mrp': item_mrp,
                'unit_mrp': inventory_item.mrp,
                'gst_rate': gst_rate
            })
        
        # Handle customer and loyalty points
        customer = None
        loyalty_points_earned = 0
        loyalty_points_redeemed = checkout_data.loyalty_points_redeemed
        loyalty_discount_amount = 0
        
        if checkout_data.customer_phone:
            customer = db.query(models.Customer).filter(models.Customer.phone == checkout_data.customer_phone).first()
            
            # If customer doesn't exist, create one
            if not customer:
                customer = models.Customer(
                    phone=checkout_data.customer_phone,
                    name=checkout_data.customer_name,
                    email=checkout_data.customer_email
                )
                db.add(customer)
                db.commit()
                db.refresh(customer)
            
            # Calculate loyalty points earned (1 point per Rs. 100 spent)
            loyalty_points_earned = int(total_mrp / 100)
            
            # Handle loyalty points redemption
            if loyalty_points_redeemed > 0:
                if customer.loyalty_points < loyalty_points_redeemed:
                    raise HTTPException(status_code=400, detail="Insufficient loyalty points")
                
                # Calculate loyalty discount (1 point = Rs. 1)
                loyalty_discount_amount = loyalty_points_redeemed
                
                # Update customer points
                customer.loyalty_points -= loyalty_points_redeemed
            
            # Update customer visit history
            customer.total_spent += total_mrp
            customer.total_orders += 1
            customer.last_visit_date = datetime.now()
        
        # Calculate bill-level discount
        total_discount = 0
        if checkout_data.discount_type == "PERCENT" and checkout_data.discount_value > 0:
            total_discount = total_mrp * (checkout_data.discount_value / 100)
        elif checkout_data.discount_type == "FIXED" and checkout_data.discount_value > 0:
            total_discount = min(checkout_data.discount_value, total_mrp)
        
        # Add loyalty discount to total discount
        total_discount += loyalty_discount_amount
        
        # Calculate final price after all discounts
        total_final_price = total_mrp - total_discount
        
        # Calculate base amount and GST (reverse calculation)
        total_base_amount = total_final_price / (1 + 12.0 / 100)  # Assuming 12% GST
        total_gst_amount = total_final_price - total_base_amount
        total_cgst_amount = total_gst_amount / 2
        total_sgst_amount = total_gst_amount / 2
        
        # Create invoice
        invoice_number = generate_invoice_number()
        db_invoice = models.Invoice(
            invoice_number=invoice_number,
            customer_id=customer.id if customer else None,
            customer_name=checkout_data.customer_name,
            customer_phone=checkout_data.customer_phone,
            customer_email=checkout_data.customer_email,
            total_mrp=total_mrp,
            total_discount=total_discount,
            total_final_price=total_final_price,
            total_base_amount=total_base_amount,
            total_gst_amount=total_gst_amount,
            total_cgst_amount=total_cgst_amount,
            total_sgst_amount=total_sgst_amount,
            payment_method=checkout_data.payment_method,
            loyalty_points_earned=loyalty_points_earned,
            loyalty_points_redeemed=loyalty_points_redeemed,
            loyalty_discount_amount=loyalty_discount_amount,
            notes=checkout_data.notes
        )
        
        db.add(db_invoice)
        db.commit()
        db.refresh(db_invoice)
        
        # Create invoice items and update inventory
        for item_data in items_to_process:
            inventory_item = item_data['inventory_item']
            
            # Calculate item-level discount proportion
            item_discount = 0
            if total_discount > 0:
                item_discount = (item_data['item_mrp'] / total_mrp) * total_discount
            
            item_final_price = item_data['item_mrp'] - item_discount
            item_base_price = item_final_price / (1 + item_data['gst_rate'] / 100)
            item_gst_amount = item_final_price - item_base_price
            item_cgst_amount = item_gst_amount / 2
            item_sgst_amount = item_gst_amount / 2
            
            # Create invoice item
            db_invoice_item = models.InvoiceItem(
                invoice_id=db_invoice.id,
                inventory_item_id=inventory_item.id,
                barcode=inventory_item.barcode,
                product_name=item_data['product_name'],
                design_number=inventory_item.design_number,
                size=inventory_item.size,
                color=inventory_item.color,
                unit_price=item_data['unit_mrp'],
                quantity=item_data['quantity'],
                total_price=item_data['item_mrp'],
                discount_amount=item_discount,
                final_price=item_final_price,
                base_price=item_base_price,
                gst_amount=item_gst_amount,
                cgst_amount=item_cgst_amount,
                sgst_amount=item_sgst_amount,
                gst_rate=item_data['gst_rate']
            )
            db.add(db_invoice_item)
            
            # Update inventory (subtract quantity)
            inventory_item.quantity -= item_data['quantity']
        
        db.commit()
        db.refresh(db_invoice)
        
        # Create loyalty transaction if customer exists and points were earned
        if customer and loyalty_points_earned > 0:
            loyalty_transaction = models.LoyaltyTransaction(
                customer_id=customer.id,
                invoice_id=db_invoice.id,
                transaction_type="EARNED",
                points=loyalty_points_earned,
                amount_spent=total_mrp,
                description=f"Earned {loyalty_points_earned} points for purchase of Rs. {total_mrp:.2f}"
            )
            db.add(loyalty_transaction)
            
            # Update customer points earned
            customer.loyalty_points += loyalty_points_earned
            db.commit()
        
        # Send WhatsApp messages if customer phone is provided
        if checkout_data.customer_phone and whatsapp_service.validate_phone_number(checkout_data.customer_phone):
            try:
                # Send thank you message with loyalty points
                thank_you_message = f"""
🎉 Thank you for your purchase!

Invoice: #{db_invoice.invoice_number}
Total: ₹{db_invoice.total_final_price:.2f}
Date: {db_invoice.created_at.strftime('%Y-%m-%d %H:%M')}

Your loyalty points: {loyalty_points_earned} earned
Total spent: ₹{total_mrp:.2f}

Thank you for choosing us! 🙏
                """.strip()
                
                whatsapp_result = whatsapp_service.send_text_message(checkout_data.customer_phone, thank_you_message)
                
                # Log the WhatsApp message
                whatsapp_log = models.WhatsAppLog(
                    customer_id=customer.id if customer else None,
                    invoice_id=db_invoice.id,
                    phone_number=checkout_data.customer_phone,
                    message_type="THANK_YOU",
                    message_content=thank_you_message,
                    status=whatsapp_result["status"],
                    interakt_message_id=whatsapp_result.get("message_id"),
                    error_message=whatsapp_result.get("error")
                )
                db.add(whatsapp_log)
                db.commit()
                
            except Exception as e:
                # Log WhatsApp error but don't fail the checkout
                logger.error(f"Error sending WhatsApp message: {str(e)}")
        
        return schemas.CheckoutResponse(
            invoice=db_invoice,
            message=f"Invoice {invoice_number} created successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating invoice: {str(e)}")

@app.get("/invoices/", response_model=List[schemas.Invoice])
def get_invoices(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get all invoices"""
    invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    return invoices

@app.get("/invoices/{invoice_id}", response_model=schemas.Invoice)
def get_invoice(
    invoice_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get a specific invoice by ID"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/invoices/number/{invoice_number}", response_model=schemas.Invoice)
def get_invoice_by_number(
    invoice_number: str, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get a specific invoice by invoice number"""
    invoice = db.query(models.Invoice).filter(models.Invoice.invoice_number == invoice_number).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/invoices/{invoice_id}/pdf")
def export_invoice_pdf(invoice_id: int, db: Session = Depends(database.get_db)):
    """Export invoice as PDF"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        return pdf_generator.generate_invoice_pdf(invoice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")



@app.get("/invoices/number/{invoice_number}/pdf")
def export_invoice_by_number_pdf(invoice_number: str, db: Session = Depends(database.get_db)):
    """Export invoice by invoice number as PDF"""
    invoice = db.query(models.Invoice).filter(models.Invoice.invoice_number == invoice_number).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        return pdf_generator.generate_invoice_pdf(invoice)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# ==================== DEALER ENDPOINTS ====================
@app.post("/dealers/", response_model=schemas.Dealer, status_code=status.HTTP_201_CREATED)
def create_dealer(
    dealer: schemas.DealerCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    db_dealer = models.Dealer(**dealer.dict())
    db.add(db_dealer)
    db.commit()
    db.refresh(db_dealer)
    return db_dealer

@app.get("/dealers/", response_model=List[schemas.Dealer])
def get_dealers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    dealers = db.query(models.Dealer).offset(skip).limit(limit).all()
    return dealers

@app.get("/dealers/{dealer_id}", response_model=schemas.Dealer)
def get_dealer(
    dealer_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    dealer = db.query(models.Dealer).filter(models.Dealer.id == dealer_id).first()
    if dealer is None:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer

# ==================== BRAND ENDPOINTS ====================
@app.post("/brands/", response_model=schemas.Brand, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand: schemas.BrandCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    db_brand = models.Brand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand

@app.get("/brands/", response_model=List[schemas.Brand])
def get_brands(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    brands = db.query(models.Brand).offset(skip).limit(limit).all()
    return brands

@app.get("/brands/{brand_id}", response_model=schemas.Brand)
def get_brand(
    brand_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

# ==================== BRAND-DEALER RELATIONSHIP ENDPOINTS ====================
@app.post("/brands/{brand_id}/dealers/{dealer_id}")
def link_dealer_to_brand(brand_id: int, dealer_id: int, db: Session = Depends(database.get_db)):
    # Check if brand and dealer exist
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    dealer = db.query(models.Dealer).filter(models.Dealer.id == dealer_id).first()
    
    if not brand or not dealer:
        raise HTTPException(status_code=404, detail="Brand or dealer not found")
    
    # Check if link already exists
    existing_link = db.query(models.DealerBrand).filter(
        models.DealerBrand.brand_id == brand_id,
        models.DealerBrand.dealer_id == dealer_id
    ).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="Link already exists")
    
    # Create the link
    link = models.DealerBrand(brand_id=brand_id, dealer_id=dealer_id)
    db.add(link)
    db.commit()
    
    return {"message": "Dealer linked to brand successfully"}

@app.delete("/brands/{brand_id}/dealers/{dealer_id}")
def unlink_dealer_from_brand(brand_id: int, dealer_id: int, db: Session = Depends(database.get_db)):
    link = db.query(models.DealerBrand).filter(
        models.DealerBrand.brand_id == brand_id,
        models.DealerBrand.dealer_id == dealer_id
    ).first()
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
    
    return {"message": "Dealer unlinked from brand successfully"}

@app.get("/brands/{brand_id}/dealers", response_model=List[schemas.Dealer])
def get_dealers_for_brand(brand_id: int, db: Session = Depends(database.get_db)):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    return brand.dealers

@app.get("/dealers/{dealer_id}/brands", response_model=List[schemas.Brand])
def get_brands_for_dealer(dealer_id: int, db: Session = Depends(database.get_db)):
    dealer = db.query(models.Dealer).filter(models.Dealer.id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    
    return dealer.brands

# ==================== PRODUCT ENDPOINTS ====================
@app.post("/products/", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    brand = db.query(models.Brand).filter(models.Brand.id == product.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    # Generate product name based on brand and type
    product_name = f"{brand.name}-{product.type}"

    db_product = models.Product(
        name=product_name,
        brand_id=product.brand_id,
        type=product.type,
        size_type=product.size_type,
        gst_rate=product.gst_rate
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.Product])
def get_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=schemas.Product)
def get_product(
    product_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# ==================== INVENTORY ENDPOINTS ====================
@app.post("/inventory/", response_model=schemas.InventoryItem, status_code=status.HTTP_201_CREATED)
def add_inventory_item(
    item: schemas.InventoryItemCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_inventory_manager_or_admin)
):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing_barcode = db.query(models.InventoryItem).filter(models.InventoryItem.barcode == item.barcode).first()
    if existing_barcode:
        raise HTTPException(status_code=400, detail="Barcode already exists")

    # Validate size based on product's size_type
    valid_sizes = SIZE_SCALES.get(product.size_type, [])
    if product.size_type != "CUSTOM" and item.size not in valid_sizes:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid size '{item.size}' for product with size_type '{product.size_type}'. Valid sizes: {valid_sizes}"
        )

    db_item = models.InventoryItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/inventory/", response_model=List[schemas.InventoryItem])
def get_inventory_items(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_inventory_manager_or_admin)
):
    items = db.query(models.InventoryItem).offset(skip).limit(limit).all()
    return items

@app.get("/inventory/product/{product_id}", response_model=List[schemas.InventoryItem])
def get_inventory_by_product(product_id: int, db: Session = Depends(database.get_db)):
    items = db.query(models.InventoryItem).filter(models.InventoryItem.product_id == product_id).all()
    return items

@app.get("/inventory/barcode/{barcode}", response_model=schemas.InventoryItem)
def get_inventory_by_barcode(barcode: str, db: Session = Depends(database.get_db)):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.barcode == barcode).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@app.get("/inventory/search/{barcode}", response_model=schemas.InventoryItem)
def search_inventory_by_barcode(barcode: str, db: Session = Depends(database.get_db)):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.barcode == barcode).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item

@app.post("/inventory/subtract")
def subtract_inventory(
    subtract_data: schemas.InventoryItemSubtract, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_inventory_manager_or_admin)
):
    item = db.query(models.InventoryItem).filter(models.InventoryItem.barcode == subtract_data.barcode).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    if item.quantity < subtract_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    item.quantity -= subtract_data.quantity
    db.commit()
    
    return {"message": f"Subtracted {subtract_data.quantity} from inventory", "remaining_quantity": item.quantity}

@app.get("/inventory/summary", response_model=List[schemas.InventorySummary])
def get_inventory_summary(db: Session = Depends(database.get_db)):
    # Get inventory summary grouped by product
    summary = db.query(
        models.Product.id.label('product_id'),
        models.Product.name.label('product_name'),
        models.Brand.name.label('brand_name'),
        func.sum(models.InventoryItem.quantity).label('total_quantity')
    ).join(
        models.Brand, models.Product.brand_id == models.Brand.id
    ).join(
        models.InventoryItem, models.Product.id == models.InventoryItem.product_id
    ).group_by(
        models.Product.id, models.Product.name, models.Brand.name
    ).all()
    
    result = []
    for row in summary:
        # Get inventory items for this product
        items = db.query(models.InventoryItem).filter(
            models.InventoryItem.product_id == row.product_id
        ).all()
        
        result.append(schemas.InventorySummary(
            product_id=row.product_id,
            product_name=row.product_name,
            brand_name=row.brand_name,
            total_quantity=row.total_quantity,
            inventory_items=items
        ))
    
    return result

# ==================== UTILITY ENDPOINTS ====================
@app.get("/size-scales")
def get_size_scales():
    """Get available size scales"""
    return SIZE_SCALES

@app.get("/product-types")
def get_product_types():
    """Get available product types"""
    return PRODUCT_TYPES 

# ==================== DASHBOARD ENDPOINTS ====================

@app.get("/dashboard/sales")
def get_sales_analytics(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get sales analytics for dashboard"""
    try:
        # Get current date and calculate date ranges
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Daily sales (today) - accounting for returns
        daily_sales = db.query(
            func.sum(models.Invoice.total_final_price).label('total_sales'),
            func.sum(models.Invoice.total_gst_amount).label('total_gst_amount'),
            func.count(models.Invoice.id).label('invoice_count')
        ).filter(
            func.date(models.Invoice.created_at) == today
        ).first()
        
        # Daily returns (today)
        daily_returns = db.query(
            func.sum(models.Return.total_return_amount).label('total_returns'),
            func.sum(models.Return.total_return_gst).label('total_return_gst')
        ).filter(
            func.date(models.Return.created_at) == today
        ).first()
        
        # Calculate net sales
        net_sales = (daily_sales.total_sales or 0) + (daily_returns.total_returns or 0)
        net_gst = (daily_sales.total_gst_amount or 0) + (daily_returns.total_return_gst or 0)
        
        # Weekly sales (last 7 days) - accounting for returns
        weekly_sales = db.query(
            func.sum(models.Invoice.total_final_price).label('total_sales'),
            func.sum(models.Invoice.total_gst_amount).label('total_gst_amount'),
            func.count(models.Invoice.id).label('invoice_count')
        ).filter(
            func.date(models.Invoice.created_at) >= week_ago
        ).first()
        
        # Weekly returns (last 7 days)
        weekly_returns = db.query(
            func.sum(models.Return.total_return_amount).label('total_returns'),
            func.sum(models.Return.total_return_gst).label('total_return_gst')
        ).filter(
            func.date(models.Return.created_at) >= week_ago
        ).first()
        
        # Calculate net weekly sales
        net_weekly_sales = (weekly_sales.total_sales or 0) + (weekly_returns.total_returns or 0)
        net_weekly_gst = (weekly_sales.total_gst_amount or 0) + (weekly_returns.total_return_gst or 0)
        
        # Monthly sales (last 30 days) - accounting for returns
        monthly_sales = db.query(
            func.sum(models.Invoice.total_final_price).label('total_sales'),
            func.sum(models.Invoice.total_gst_amount).label('total_gst_amount'),
            func.count(models.Invoice.id).label('invoice_count')
        ).filter(
            func.date(models.Invoice.created_at) >= month_ago
        ).first()
        
        # Monthly returns (last 30 days)
        monthly_returns = db.query(
            func.sum(models.Return.total_return_amount).label('total_returns'),
            func.sum(models.Return.total_return_gst).label('total_return_gst')
        ).filter(
            func.date(models.Return.created_at) >= month_ago
        ).first()
        
        # Calculate net monthly sales
        net_monthly_sales = (monthly_sales.total_sales or 0) + (monthly_returns.total_returns or 0)
        net_monthly_gst = (monthly_sales.total_gst_amount or 0) + (monthly_returns.total_return_gst or 0)
        
        # Sales trend (last 7 days daily breakdown) - accounting for returns
        sales_trend = db.query(
            func.date(models.Invoice.created_at).label('date'),
            func.sum(models.Invoice.total_final_price).label('sales'),
            func.sum(models.Invoice.total_gst_amount).label('gst'),
            func.count(models.Invoice.id).label('invoices')
        ).filter(
            func.date(models.Invoice.created_at) >= week_ago
        ).group_by(
            func.date(models.Invoice.created_at)
        ).order_by(
            func.date(models.Invoice.created_at)
        ).all()
        
        # Returns trend (last 7 days daily breakdown)
        returns_trend = db.query(
            func.date(models.Return.created_at).label('date'),
            func.sum(models.Return.total_return_amount).label('returns'),
            func.sum(models.Return.total_return_gst).label('return_gst')
        ).filter(
            func.date(models.Return.created_at) >= week_ago
        ).group_by(
            func.date(models.Return.created_at)
        ).order_by(
            func.date(models.Return.created_at)
        ).all()
        
        # Combine sales and returns for net trend
        trend_dict = {}
        
        # Add sales data
        for item in sales_trend:
            trend_dict[item.date] = {
                'sales': float(item.sales or 0),
                'gst': float(item.gst or 0),
                'invoices': item.invoices or 0,
                'returns': 0,
                'return_gst': 0
            }
        
        # Add returns data
        for item in returns_trend:
            if item.date in trend_dict:
                trend_dict[item.date]['returns'] = float(item.returns or 0)
                trend_dict[item.date]['return_gst'] = float(item.return_gst or 0)
            else:
                trend_dict[item.date] = {
                    'sales': 0,
                    'gst': 0,
                    'invoices': 0,
                    'returns': float(item.returns or 0),
                    'return_gst': float(item.return_gst or 0)
                }
        
        # Calculate net values
        net_trend = []
        for date, data in trend_dict.items():
            net_sales = data['sales'] + data['returns']
            net_gst = data['gst'] + data['return_gst']
            net_trend.append({
                'date': str(date),
                'sales': net_sales,
                'gst': net_gst,
                'invoices': data['invoices']
            })
        
        return {
            "daily": {
                "sales": float(net_sales),
                "gst": float(net_gst),
                "invoices": daily_sales.invoice_count or 0
            },
            "weekly": {
                "sales": float(net_weekly_sales),
                "gst": float(net_weekly_gst),
                "invoices": weekly_sales.invoice_count or 0
            },
            "monthly": {
                "sales": float(net_monthly_sales),
                "gst": float(net_monthly_gst),
                "invoices": monthly_sales.invoice_count or 0
            },
            "trend": net_trend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sales analytics: {str(e)}")

@app.get("/dashboard/top-products")
def get_top_products(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get top 10 selling products"""
    try:
        # Get top products by quantity sold
        top_products = db.query(
            models.Product.name.label('product_name'),
            models.Product.id.label('product_id'),
            func.sum(models.InvoiceItem.quantity).label('total_quantity'),
            func.sum(models.InvoiceItem.final_price).label('total_revenue'),
            func.count(models.InvoiceItem.id).label('times_sold')
        ).join(
            models.InvoiceItem, models.Product.id == models.InvoiceItem.inventory_item_id
        ).join(
            models.InventoryItem, models.InvoiceItem.inventory_item_id == models.InventoryItem.id
        ).filter(
            models.InventoryItem.product_id == models.Product.id
        ).group_by(
            models.Product.id, models.Product.name
        ).order_by(
            desc(func.sum(models.InvoiceItem.quantity))
        ).limit(10).all()
        
        return [
            {
                "product_name": item.product_name,
                "product_id": item.product_id,
                "total_quantity": int(item.total_quantity or 0),
                "total_revenue": float(item.total_revenue or 0),
                "times_sold": item.times_sold or 0
            }
            for item in top_products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting top products: {str(e)}")

@app.get("/dashboard/inventory-aging")
def get_inventory_aging(
    days: int = 30, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get inventory items not sold in the past X days"""
    try:
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get inventory items that haven't been sold recently
        aging_items = db.query(
            models.InventoryItem.id,
            models.InventoryItem.barcode,
            models.InventoryItem.design_number,
            models.InventoryItem.size,
            models.InventoryItem.color,
            models.InventoryItem.mrp,
            models.InventoryItem.quantity,
            models.InventoryItem.created_at,
            models.Product.name.label('product_name')
        ).join(
            models.Product, models.InventoryItem.product_id == models.Product.id
        ).outerjoin(
            models.InvoiceItem, models.InventoryItem.id == models.InvoiceItem.inventory_item_id
        ).filter(
            models.InventoryItem.quantity > 0
        ).group_by(
            models.InventoryItem.id, models.Product.name
        ).having(
            func.max(models.InvoiceItem.created_at) < cutoff_date
        ).order_by(
            models.InventoryItem.created_at
        ).all()
        
        return [
            {
                "id": item.id,
                "barcode": item.barcode,
                "product_name": item.product_name,
                "design_number": item.design_number,
                "size": item.size,
                "color": item.color,
                "mrp": float(item.mrp),
                "quantity": item.quantity,
                "created_at": item.created_at.isoformat(),
                "days_old": (datetime.now() - item.created_at).days
            }
            for item in aging_items
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting inventory aging: {str(e)}")

@app.get("/dashboard/gst-summary")
def get_gst_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get GST collection summary"""
    try:
        # Get GST summary for different periods
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Daily GST - accounting for returns
        daily_gst = db.query(
            func.sum(models.Invoice.total_cgst_amount).label('cgst'),
            func.sum(models.Invoice.total_sgst_amount).label('sgst'),
            func.sum(models.Invoice.total_gst_amount).label('total_gst')
        ).filter(
            func.date(models.Invoice.created_at) == today
        ).first()
        
        # Daily return GST
        daily_return_gst = db.query(
            func.sum(models.Return.total_return_cgst).label('return_cgst'),
            func.sum(models.Return.total_return_sgst).label('return_sgst'),
            func.sum(models.Return.total_return_gst).label('return_total_gst')
        ).filter(
            func.date(models.Return.created_at) == today
        ).first()
        
        # Calculate net GST
        net_daily_cgst = (daily_gst.cgst or 0) + (daily_return_gst.return_cgst or 0)
        net_daily_sgst = (daily_gst.sgst or 0) + (daily_return_gst.return_sgst or 0)
        net_daily_total_gst = (daily_gst.total_gst or 0) + (daily_return_gst.return_total_gst or 0)
        
        # Weekly GST - accounting for returns
        weekly_gst = db.query(
            func.sum(models.Invoice.total_cgst_amount).label('cgst'),
            func.sum(models.Invoice.total_sgst_amount).label('sgst'),
            func.sum(models.Invoice.total_gst_amount).label('total_gst')
        ).filter(
            func.date(models.Invoice.created_at) >= week_ago
        ).first()
        
        # Weekly return GST
        weekly_return_gst = db.query(
            func.sum(models.Return.total_return_cgst).label('return_cgst'),
            func.sum(models.Return.total_return_sgst).label('return_sgst'),
            func.sum(models.Return.total_return_gst).label('return_total_gst')
        ).filter(
            func.date(models.Return.created_at) >= week_ago
        ).first()
        
        # Calculate net weekly GST
        net_weekly_cgst = (weekly_gst.cgst or 0) + (weekly_return_gst.return_cgst or 0)
        net_weekly_sgst = (weekly_gst.sgst or 0) + (weekly_return_gst.return_sgst or 0)
        net_weekly_total_gst = (weekly_gst.total_gst or 0) + (weekly_return_gst.return_total_gst or 0)
        
        # Monthly GST - accounting for returns
        monthly_gst = db.query(
            func.sum(models.Invoice.total_cgst_amount).label('cgst'),
            func.sum(models.Invoice.total_sgst_amount).label('sgst'),
            func.sum(models.Invoice.total_gst_amount).label('total_gst')
        ).filter(
            func.date(models.Invoice.created_at) >= month_ago
        ).first()
        
        # Monthly return GST
        monthly_return_gst = db.query(
            func.sum(models.Return.total_return_cgst).label('return_cgst'),
            func.sum(models.Return.total_return_sgst).label('return_sgst'),
            func.sum(models.Return.total_return_gst).label('return_total_gst')
        ).filter(
            func.date(models.Return.created_at) >= month_ago
        ).first()
        
        # Calculate net monthly GST
        net_monthly_cgst = (monthly_gst.cgst or 0) + (monthly_return_gst.return_cgst or 0)
        net_monthly_sgst = (monthly_gst.sgst or 0) + (monthly_return_gst.return_sgst or 0)
        net_monthly_total_gst = (monthly_gst.total_gst or 0) + (monthly_return_gst.return_total_gst or 0)
        
        return {
            "daily": {
                "cgst": float(net_daily_cgst),
                "sgst": float(net_daily_sgst),
                "total": float(net_daily_total_gst)
            },
            "weekly": {
                "cgst": float(net_weekly_cgst),
                "sgst": float(net_weekly_sgst),
                "total": float(net_weekly_total_gst)
            },
            "monthly": {
                "cgst": float(net_monthly_cgst),
                "sgst": float(net_monthly_sgst),
                "total": float(net_monthly_total_gst)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting GST summary: {str(e)}") 

def generate_return_number():
    """Generate a unique return number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"RET-{timestamp}-{random_suffix}"

# ==================== RETURN ENDPOINTS ====================

@app.get("/returns/invoice/{invoice_number}")
def get_invoice_for_return(
    invoice_number: str, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get invoice details for return processing"""
    invoice = db.query(models.Invoice).filter(models.Invoice.invoice_number == invoice_number).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Check if invoice has already been returned
    existing_returns = db.query(models.Return).filter(models.Return.invoice_id == invoice.id).all()
    
    return {
        "invoice": invoice,
        "items": invoice.items,
        "existing_returns": existing_returns,
        "can_return": len(existing_returns) == 0  # Only allow returns if no previous returns
    }

@app.post("/returns/", response_model=schemas.ReturnResponse)
def create_return(
    return_data: schemas.ReturnRequest, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Create a new return"""
    try:
        # Find the invoice
        invoice = db.query(models.Invoice).filter(models.Invoice.invoice_number == return_data.invoice_number).first()
        if invoice is None:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Check if invoice has already been returned
        existing_returns = db.query(models.Return).filter(models.Return.invoice_id == invoice.id).all()
        if existing_returns:
            raise HTTPException(status_code=400, detail="Invoice has already been returned")
        
        # Validate return items
        total_return_amount = 0
        total_return_gst = 0
        total_return_cgst = 0
        total_return_sgst = 0
        return_items = []
        
        for item_request in return_data.items:
            # Find the invoice item
            invoice_item = db.query(models.InvoiceItem).filter(
                models.InvoiceItem.id == item_request.invoice_item_id,
                models.InvoiceItem.invoice_id == invoice.id
            ).first()
            
            if invoice_item is None:
                raise HTTPException(status_code=404, detail=f"Invoice item {item_request.invoice_item_id} not found")
            
            if item_request.return_quantity > invoice_item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Return quantity ({item_request.return_quantity}) cannot exceed original quantity ({invoice_item.quantity})"
                )
            
            # Calculate return amounts (negative values)
            item_return_amount = -(invoice_item.final_price / invoice_item.quantity) * item_request.return_quantity
            item_return_gst = -(invoice_item.gst_amount / invoice_item.quantity) * item_request.return_quantity
            item_return_cgst = -(invoice_item.cgst_amount / invoice_item.quantity) * item_request.return_quantity
            item_return_sgst = -(invoice_item.sgst_amount / invoice_item.quantity) * item_request.return_quantity
            
            total_return_amount += item_return_amount
            total_return_gst += item_return_gst
            total_return_cgst += item_return_cgst
            total_return_sgst += item_return_sgst
            
            return_items.append({
                'invoice_item': invoice_item,
                'return_quantity': item_request.return_quantity,
                'return_amount': item_return_amount,
                'return_gst': item_return_gst,
                'return_cgst': item_return_cgst,
                'return_sgst': item_return_sgst
            })
        
        # Validate return method and amounts
        if return_data.return_method == "CASH":
            if return_data.cash_refund != abs(total_return_amount):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cash refund amount ({return_data.cash_refund}) must equal return amount ({abs(total_return_amount)})"
                )
        elif return_data.return_method == "WALLET":
            if return_data.wallet_credit != abs(total_return_amount):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Wallet credit amount ({return_data.wallet_credit}) must equal return amount ({abs(total_return_amount)})"
                )
        elif return_data.return_method == "STORE_CREDIT":
            if return_data.wallet_credit != abs(total_return_amount):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Store credit amount ({return_data.wallet_credit}) must equal return amount ({abs(total_return_amount)})"
                )
        
        # Create return record
        db_return = models.Return(
            return_number=generate_return_number(),
            invoice_id=invoice.id,
            invoice_number=invoice.invoice_number,
            customer_name=invoice.customer_name,
            customer_phone=invoice.customer_phone,
            customer_email=invoice.customer_email,
            return_reason=return_data.return_reason,
            return_method=return_data.return_method,
            total_return_amount=total_return_amount,
            total_return_gst=total_return_gst,
            total_return_cgst=total_return_cgst,
            total_return_sgst=total_return_sgst,
            wallet_credit=return_data.wallet_credit,
            cash_refund=return_data.cash_refund,
            notes=return_data.notes
        )
        
        db.add(db_return)
        db.commit()
        db.refresh(db_return)
        
        # Create return items and update inventory
        for item_data in return_items:
            invoice_item = item_data['invoice_item']
            
            # Create return item
            db_return_item = models.ReturnItem(
                return_id=db_return.id,
                invoice_item_id=invoice_item.id,
                inventory_item_id=invoice_item.inventory_item_id,
                barcode=invoice_item.barcode,
                product_name=invoice_item.product_name,
                design_number=invoice_item.design_number,
                size=invoice_item.size,
                color=invoice_item.color,
                original_quantity=invoice_item.quantity,
                return_quantity=item_data['return_quantity'],
                unit_price=invoice_item.unit_price,
                total_return_price=item_data['return_amount'],
                return_gst_amount=item_data['return_gst'],
                return_cgst_amount=item_data['return_cgst'],
                return_sgst_amount=item_data['return_sgst'],
                gst_rate=invoice_item.gst_rate
            )
            db.add(db_return_item)
            
            # Update inventory (add back to stock)
            inventory_item = db.query(models.InventoryItem).filter(
                models.InventoryItem.id == invoice_item.inventory_item_id
            ).first()
            
            if inventory_item:
                inventory_item.quantity += item_data['return_quantity']
        
        db.commit()
        db.refresh(db_return)
        
        return schemas.ReturnResponse(
            return_record=db_return,
            message=f"Return {db_return.return_number} created successfully!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating return: {str(e)}")

@app.get("/returns/", response_model=List[schemas.Return])
def get_returns(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """Get all returns"""
    returns = db.query(models.Return).offset(skip).limit(limit).all()
    return returns

@app.get("/returns/{return_id}", response_model=schemas.Return)
def get_return(return_id: int, db: Session = Depends(database.get_db)):
    """Get a specific return by ID"""
    return_record = db.query(models.Return).filter(models.Return.id == return_id).first()
    if return_record is None:
        raise HTTPException(status_code=404, detail="Return not found")
    return return_record

@app.get("/returns/number/{return_number}", response_model=schemas.Return)
def get_return_by_number(return_number: str, db: Session = Depends(database.get_db)):
    """Get a specific return by return number"""
    return_record = db.query(models.Return).filter(models.Return.return_number == return_number).first()
    if return_record is None:
        raise HTTPException(status_code=404, detail="Return not found")
    return return_record

@app.get("/returns/{return_id}/pdf")
def export_return_pdf(return_id: int, db: Session = Depends(database.get_db)):
    """Export return as PDF"""
    return_record = db.query(models.Return).filter(models.Return.id == return_id).first()
    if return_record is None:
        raise HTTPException(status_code=404, detail="Return not found")
    
    try:
        return pdf_generator.generate_return_pdf(return_record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@app.get("/returns/number/{return_number}/pdf")
def export_return_by_number_pdf(return_number: str, db: Session = Depends(database.get_db)):
    """Export return by return number as PDF"""
    return_record = db.query(models.Return).filter(models.Return.return_number == return_number).first()
    if return_record is None:
        raise HTTPException(status_code=404, detail="Return not found")
    
    try:
        return pdf_generator.generate_return_pdf(return_record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# ==================== ML FORECASTING ENDPOINTS ====================
@app.get("/ml/inventory-analysis")
def get_inventory_analysis(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get comprehensive inventory analysis with ML forecasting"""
    try:
        optimizer = InventoryOptimizer()
        analysis = optimizer.get_inventory_analysis(db)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in inventory analysis: {str(e)}")

@app.get("/ml/product-analysis/{product_id}")
def get_product_analysis(
    product_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get detailed ML analysis for a specific product"""
    try:
        optimizer = InventoryOptimizer()
        analysis = optimizer.analyze_product(db, product_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Product not found")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in product analysis: {str(e)}")

@app.get("/ml/reorder-suggestions")
def get_reorder_suggestions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get reorder suggestions based on ML forecasting"""
    try:
        optimizer = InventoryOptimizer()
        suggestions = optimizer.get_reorder_suggestions(db)
        return {
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting reorder suggestions: {str(e)}")

@app.get("/ml/stock-alerts")
def get_stock_alerts(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get stock alerts for deadstock, slow-moving, and out-of-stock items"""
    try:
        optimizer = InventoryOptimizer()
        analysis = optimizer.get_inventory_analysis(db)
        
        alerts = {
            "deadstock": {
                "count": analysis["deadstock_count"],
                "items": analysis["deadstock_items"]
            },
            "slow_moving": {
                "count": analysis["slow_moving_count"],
                "items": analysis["slow_moving_items"]
            },
            "out_of_stock": {
                "count": analysis["out_of_stock_count"],
                "items": analysis["out_of_stock_items"]
            }
        }
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stock alerts: {str(e)}")

# ==================== CASH REGISTER ENDPOINTS ====================
@app.post("/cash-register/open", response_model=schemas.CashRegister, status_code=status.HTTP_201_CREATED)
def open_cash_register(
    cash_register: schemas.CashRegisterCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Open cash register for the day"""
    try:
        # Check if cash register is already open for today
        today = datetime.now().date()
        existing_register = db.query(models.CashRegister).filter(
            func.date(models.CashRegister.date) == today
        ).first()
        
        if existing_register:
            raise HTTPException(status_code=400, detail="Cash register already opened for today")
        
        # Create new cash register entry
        db_cash_register = models.CashRegister(
            date=datetime.now(),
            opening_balance=cash_register.opening_balance,
            notes=cash_register.notes
        )
        db.add(db_cash_register)
        db.commit()
        db.refresh(db_cash_register)
        
        return db_cash_register
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error opening cash register: {str(e)}")

@app.post("/cash-register/close", response_model=schemas.CashRegister)
def close_cash_register(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Close cash register for the day"""
    try:
        today = datetime.now().date()
        cash_register = db.query(models.CashRegister).filter(
            func.date(models.CashRegister.date) == today
        ).first()
        
        if not cash_register:
            raise HTTPException(status_code=404, detail="No cash register opened for today")
        
        # Calculate totals from sales and returns
        today_sales = db.query(func.sum(models.Invoice.total_final_price)).filter(
            and_(
                func.date(models.Invoice.created_at) == today,
                models.Invoice.payment_method == "CASH"
            )
        ).scalar() or 0.0
        
        today_returns = db.query(func.sum(models.Return.cash_refund)).filter(
            and_(
                func.date(models.Return.created_at) == today,
                models.Return.return_method == "CASH"
            )
        ).scalar() or 0.0
        
        # Calculate total expenses
        total_expenses = db.query(func.sum(models.CashExpense.amount)).filter(
            models.CashExpense.cash_register_id == cash_register.id
        ).scalar() or 0.0
        
        # Calculate closing balance
        closing_balance = cash_register.opening_balance + today_sales - today_returns - total_expenses
        
        # Update cash register
        cash_register.closing_balance = closing_balance
        cash_register.total_sales = today_sales
        cash_register.total_returns = today_returns
        cash_register.total_expenses = total_expenses
        cash_register.updated_at = datetime.now()
        
        db.commit()
        db.refresh(cash_register)
        
        return cash_register
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error closing cash register: {str(e)}")

@app.get("/cash-register/status", response_model=schemas.CashRegisterSummary)
def get_cash_register_status(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get current cash register status"""
    try:
        today = datetime.now().date()
        cash_register = db.query(models.CashRegister).filter(
            func.date(models.CashRegister.date) == today
        ).first()
        
        if not cash_register:
            raise HTTPException(status_code=404, detail="No cash register opened for today")
        
        # Get today's sales and returns
        today_sales = db.query(func.sum(models.Invoice.total_final_price)).filter(
            and_(
                func.date(models.Invoice.created_at) == today,
                models.Invoice.payment_method == "CASH"
            )
        ).scalar() or 0.0
        
        today_returns = db.query(func.sum(models.Return.cash_refund)).filter(
            and_(
                func.date(models.Return.created_at) == today,
                models.Return.return_method == "CASH"
            )
        ).scalar() or 0.0
        
        # Get expenses
        expenses = db.query(models.CashExpense).filter(
            models.CashExpense.cash_register_id == cash_register.id
        ).all()
        
        total_expenses = sum(expense.amount for expense in expenses)
        net_cash = cash_register.opening_balance + today_sales - today_returns - total_expenses
        
        return {
            "date": today.isoformat(),
            "opening_balance": cash_register.opening_balance,
            "closing_balance": net_cash,
            "total_sales": today_sales,
            "total_returns": today_returns,
            "total_expenses": total_expenses,
            "net_cash": net_cash,
            "expenses": expenses
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cash register status: {str(e)}")

@app.post("/cash-register/expenses", response_model=schemas.CashExpense, status_code=status.HTTP_201_CREATED)
def add_expense(
    expense: schemas.CashExpenseCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Add an expense to the cash register"""
    try:
        today = datetime.now().date()
        cash_register = db.query(models.CashRegister).filter(
            func.date(models.CashRegister.date) == today
        ).first()
        
        if not cash_register:
            raise HTTPException(status_code=404, detail="No cash register opened for today")
        
        db_expense = models.CashExpense(
            cash_register_id=cash_register.id,
            date=datetime.now(),
            category=expense.category,
            description=expense.description,
            amount=expense.amount
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        
        return db_expense
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding expense: {str(e)}")

@app.get("/cash-register/history", response_model=List[schemas.CashRegister])
def get_cash_register_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get cash register history"""
    try:
        query = db.query(models.CashRegister)
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(func.date(models.CashRegister.date) >= start)
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(func.date(models.CashRegister.date) <= end)
        
        cash_registers = query.order_by(models.CashRegister.date.desc()).all()
        return cash_registers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cash register history: {str(e)}")

@app.get("/cash-register/export/{date}")
def export_cash_register(
    date: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Export cash register log for a specific date"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        cash_register = db.query(models.CashRegister).filter(
            func.date(models.CashRegister.date) == target_date
        ).first()
        
        if not cash_register:
            raise HTTPException(status_code=404, detail="No cash register found for this date")
        
        # Get sales and returns for the date
        sales = db.query(models.Invoice).filter(
            and_(
                func.date(models.Invoice.created_at) == target_date,
                models.Invoice.payment_method == "CASH"
            )
        ).all()
        
        returns = db.query(models.Return).filter(
            and_(
                func.date(models.Return.created_at) == target_date,
                models.Return.return_method == "CASH"
            )
        ).all()
        
        expenses = db.query(models.CashExpense).filter(
            models.CashExpense.cash_register_id == cash_register.id
        ).all()
        
        # Create export data
        export_data = {
            "date": target_date.isoformat(),
            "cash_register": {
                "opening_balance": cash_register.opening_balance,
                "closing_balance": cash_register.closing_balance,
                "total_sales": cash_register.total_sales,
                "total_returns": cash_register.total_returns,
                "total_expenses": cash_register.total_expenses,
                "notes": cash_register.notes
            },
            "sales": [
                {
                    "invoice_number": sale.invoice_number,
                    "customer_name": sale.customer_name,
                    "amount": sale.total_final_price,
                    "time": sale.created_at.isoformat()
                }
                for sale in sales
            ],
            "returns": [
                {
                    "return_number": ret.return_number,
                    "customer_name": ret.customer_name,
                    "amount": ret.cash_refund,
                    "time": ret.created_at.isoformat()
                }
                for ret in returns
            ],
            "expenses": [
                {
                    "category": expense.category,
                    "description": expense.description,
                    "amount": expense.amount,
                    "time": expense.created_at.isoformat()
                }
                for expense in expenses
            ]
        }
        
        return export_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting cash register: {str(e)}")

# ==================== LOYALTY SYSTEM ENDPOINTS ====================
@app.post("/customers/", response_model=schemas.Customer, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Create a new customer"""
    try:
        # Check if customer with phone already exists
        existing_customer = db.query(models.Customer).filter(models.Customer.phone == customer.phone).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")
        
        db_customer = models.Customer(**customer.dict())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating customer: {str(e)}")

@app.get("/customers/", response_model=List[schemas.Customer])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get all customers"""
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(
    customer_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get a specific customer"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/customers/phone/{phone}", response_model=schemas.Customer)
def get_customer_by_phone(
    phone: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get customer by phone number"""
    customer = db.query(models.Customer).filter(models.Customer.phone == phone).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/customers/{customer_id}/loyalty", response_model=schemas.CustomerLoyaltyInfo)
def get_customer_loyalty_info(
    customer_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get customer loyalty information"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get recent loyalty transactions
    recent_transactions = db.query(models.LoyaltyTransaction).filter(
        models.LoyaltyTransaction.customer_id == customer_id
    ).order_by(models.LoyaltyTransaction.created_at.desc()).limit(10).all()
    
    return {
        "customer": customer,
        "loyalty_points": customer.loyalty_points,
        "total_spent": customer.total_spent,
        "total_orders": customer.total_orders,
        "recent_transactions": recent_transactions
    }

@app.post("/loyalty/redemption", response_model=schemas.LoyaltyRedemptionResponse)
def redeem_loyalty_points(
    redemption: schemas.LoyaltyRedemptionRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Redeem loyalty points for discount"""
    try:
        customer = db.query(models.Customer).filter(models.Customer.phone == redemption.customer_phone).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        if customer.loyalty_points < redemption.points_to_redeem:
            raise HTTPException(status_code=400, detail="Insufficient loyalty points")
        
        if redemption.points_to_redeem <= 0:
            raise HTTPException(status_code=400, detail="Points to redeem must be positive")
        
        # Calculate discount amount (1 point = Rs. 1)
        discount_amount = redemption.points_to_redeem
        
        # Update customer points
        customer.loyalty_points -= redemption.points_to_redeem
        
        # Create loyalty transaction
        loyalty_transaction = models.LoyaltyTransaction(
            customer_id=customer.id,
            transaction_type="REDEEMED",
            points=-redemption.points_to_redeem,
            discount_amount=discount_amount,
            description=f"Redeemed {redemption.points_to_redeem} points for Rs. {discount_amount} discount"
        )
        db.add(loyalty_transaction)
        db.commit()
        db.refresh(customer)
        
        return {
            "customer": customer,
            "points_redeemed": redemption.points_to_redeem,
            "discount_amount": discount_amount,
            "remaining_points": customer.loyalty_points
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error redeeming points: {str(e)}")

@app.get("/loyalty/transactions/{customer_id}", response_model=List[schemas.LoyaltyTransaction])
def get_customer_loyalty_transactions(
    customer_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get customer loyalty transaction history"""
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    transactions = db.query(models.LoyaltyTransaction).filter(
        models.LoyaltyTransaction.customer_id == customer_id
    ).order_by(models.LoyaltyTransaction.created_at.desc()).all()
    
    return transactions

# ==================== CRM ENDPOINTS ====================
@app.post("/crm/search", response_model=schemas.CustomerSearchResponse)
def search_customers(
    search_request: schemas.CustomerSearchRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Search customers by name or phone number"""
    try:
        search_term = search_request.search_term.strip()
        if not search_term:
            return {"customers": [], "total_count": 0}
        
        # Search by phone number (exact match)
        phone_customers = db.query(models.Customer).filter(
            models.Customer.phone == search_term
        ).all()
        
        # Search by name (partial match, case insensitive)
        name_customers = db.query(models.Customer).filter(
            and_(
                models.Customer.name.isnot(None),
                func.lower(models.Customer.name).contains(func.lower(search_term))
            )
        ).all()
        
        # Combine and remove duplicates
        all_customers = phone_customers + name_customers
        unique_customers = list({customer.id: customer for customer in all_customers}.values())
        
        return {
            "customers": unique_customers,
            "total_count": len(unique_customers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching customers: {str(e)}")

@app.get("/crm/customers/{customer_id}/visits", response_model=schemas.CustomerVisitHistory)
def get_customer_visit_history(
    customer_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Get customer visit history with detailed invoice information"""
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get all invoices for this customer
        invoices = db.query(models.Invoice).filter(
            models.Invoice.customer_id == customer_id
        ).order_by(models.Invoice.created_at.desc()).all()
        
        total_visits = len(invoices)
        total_spent = sum(invoice.total_final_price for invoice in invoices)
        average_order_value = total_spent / total_visits if total_visits > 0 else 0
        last_visit_date = invoices[0].created_at if invoices else None
        
        return {
            "customer": customer,
            "invoices": invoices,
            "total_visits": total_visits,
            "total_spent": total_spent,
            "average_order_value": average_order_value,
            "last_visit_date": last_visit_date
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting customer visit history: {str(e)}")

@app.get("/crm/customers/export")
def export_customers_csv(
    include_phone: bool = True,
    include_email: bool = True,
    include_address: bool = True,
    include_loyalty: bool = True,
    include_visit_history: bool = True,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Export customers to CSV for marketing use"""
    try:
        customers = db.query(models.Customer).all()
        
        # Prepare CSV data
        csv_data = []
        headers = ["ID", "Name"]
        
        if include_phone:
            headers.append("Phone")
        if include_email:
            headers.append("Email")
        if include_address:
            headers.append("Address")
        if include_loyalty:
            headers.extend(["Loyalty Points", "Total Spent", "Total Orders"])
        if include_visit_history:
            headers.append("Last Visit Date")
        
        headers.extend(["Created Date"])
        csv_data.append(headers)
        
        for customer in customers:
            row = [customer.id, customer.name or "Unknown"]
            
            if include_phone:
                row.append(customer.phone)
            if include_email:
                row.append(customer.email or "")
            if include_address:
                row.append(customer.address or "")
            if include_loyalty:
                row.extend([customer.loyalty_points, customer.total_spent, customer.total_orders])
            if include_visit_history:
                row.append(customer.last_visit_date.strftime("%Y-%m-%d") if customer.last_visit_date else "")
            
            row.append(customer.created_at.strftime("%Y-%m-%d"))
            csv_data.append(row)
        
        # Convert to CSV string
        csv_content = "\n".join([",".join([str(cell) for cell in row]) for row in csv_data])
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=customers_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting customers: {str(e)}")

@app.get("/crm/analytics")
def get_crm_analytics(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get CRM analytics and insights"""
    try:
        # Total customers
        total_customers = db.query(models.Customer).count()
        
        # Customers with names vs anonymous
        named_customers = db.query(models.Customer).filter(models.Customer.name.isnot(None)).count()
        anonymous_customers = total_customers - named_customers
        
        # Top customers by spending
        top_customers = db.query(models.Customer).order_by(
            models.Customer.total_spent.desc()
        ).limit(10).all()
        
        # Recent customers (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_customers = db.query(models.Customer).filter(
            models.Customer.created_at >= thirty_days_ago
        ).count()
        
        # Average customer metrics
        avg_spent = db.query(func.avg(models.Customer.total_spent)).scalar() or 0
        avg_orders = db.query(func.avg(models.Customer.total_orders)).scalar() or 0
        avg_loyalty_points = db.query(func.avg(models.Customer.loyalty_points)).scalar() or 0
        
        return {
            "total_customers": total_customers,
            "named_customers": named_customers,
            "anonymous_customers": anonymous_customers,
            "recent_customers_30_days": recent_customers,
            "average_spent": float(avg_spent),
            "average_orders": float(avg_orders),
            "average_loyalty_points": float(avg_loyalty_points),
            "top_customers": [
                {
                    "id": customer.id,
                    "name": customer.name or "Unknown",
                    "phone": customer.phone,
                    "total_spent": customer.total_spent,
                    "total_orders": customer.total_orders
                }
                for customer in top_customers
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting CRM analytics: {str(e)}")

# ==================== WHATSAPP MESSAGING ENDPOINTS ====================
@app.post("/whatsapp/templates/", response_model=schemas.WhatsAppTemplate, status_code=status.HTTP_201_CREATED)
def create_whatsapp_template(
    template: schemas.WhatsAppTemplateCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Create a new WhatsApp message template"""
    try:
        db_template = models.WhatsAppTemplate(**template.dict())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

@app.get("/whatsapp/templates/", response_model=List[schemas.WhatsAppTemplate])
def get_whatsapp_templates(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get all WhatsApp templates"""
    try:
        templates = db.query(models.WhatsAppTemplate).all()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@app.get("/whatsapp/templates/{template_id}", response_model=schemas.WhatsAppTemplate)
def get_whatsapp_template(
    template_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get a specific WhatsApp template"""
    try:
        template = db.query(models.WhatsAppTemplate).filter(models.WhatsAppTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching template: {str(e)}")

@app.put("/whatsapp/templates/{template_id}", response_model=schemas.WhatsAppTemplate)
def update_whatsapp_template(
    template_id: int,
    template_update: schemas.WhatsAppTemplateCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Update a WhatsApp template"""
    try:
        db_template = db.query(models.WhatsAppTemplate).filter(models.WhatsAppTemplate.id == template_id).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        for key, value in template_update.dict().items():
            setattr(db_template, key, value)
        
        db.commit()
        db.refresh(db_template)
        return db_template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating template: {str(e)}")

@app.delete("/whatsapp/templates/{template_id}")
def delete_whatsapp_template(
    template_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Delete a WhatsApp template"""
    try:
        db_template = db.query(models.WhatsAppTemplate).filter(models.WhatsAppTemplate.id == template_id).first()
        if not db_template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        db.delete(db_template)
        db.commit()
        return {"message": "Template deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting template: {str(e)}")

@app.post("/whatsapp/send-message")
def send_whatsapp_message(
    phone_number: str,
    message: str,
    customer_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Send a WhatsApp message to a customer"""
    try:
        # Validate phone number
        if not whatsapp_service.validate_phone_number(phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        # Send message via WhatsApp service
        result = whatsapp_service.send_text_message(phone_number, message)
        
        # Log the message
        log_entry = models.WhatsAppLog(
            customer_id=customer_id,
            invoice_id=invoice_id,
            phone_number=phone_number,
            message_type="CUSTOM",
            message_content=message,
            status=result["status"],
            interakt_message_id=result.get("message_id"),
            error_message=result.get("error")
        )
        db.add(log_entry)
        db.commit()
        
        return {
            "success": result["success"],
            "message_id": result.get("message_id"),
            "status": result["status"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending WhatsApp message: {str(e)}")

@app.post("/whatsapp/send-invoice")
def send_invoice_whatsapp(
    invoice_id: int,
    phone_number: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_cashier_or_admin)
):
    """Send invoice PDF via WhatsApp"""
    try:
        # Get invoice
        invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        
        # Generate PDF
        pdf_content = pdf_generator.generate_invoice_pdf(invoice)
        
        # For now, we'll send a text summary since media upload requires file hosting
        # In production, you'd upload the PDF to a cloud service and send the URL
        message = f"""
🎉 Thank you for your purchase!

Invoice: #{invoice.invoice_number}
Total: ₹{invoice.total_final_price:.2f}
Date: {invoice.created_at.strftime('%Y-%m-%d %H:%M')}

Your loyalty points: {invoice.loyalty_points_earned} earned
Total spent: ₹{invoice.total_mrp:.2f}

Thank you for choosing us! 🙏
        """.strip()
        
        # Send message
        result = whatsapp_service.send_text_message(phone_number, message)
        
        # Log the message
        log_entry = models.WhatsAppLog(
            customer_id=invoice.customer_id,
            invoice_id=invoice_id,
            phone_number=phone_number,
            message_type="INVOICE",
            message_content=message,
            status=result["status"],
            interakt_message_id=result.get("message_id"),
            error_message=result.get("error")
        )
        db.add(log_entry)
        db.commit()
        
        return {
            "success": result["success"],
            "message_id": result.get("message_id"),
            "status": result["status"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending invoice WhatsApp: {str(e)}")

@app.post("/whatsapp/broadcast")
def send_broadcast_message(
    broadcast_request: schemas.WhatsAppBroadcastRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Send broadcast message to multiple customers"""
    try:
        # Get template
        template = db.query(models.WhatsAppTemplate).filter(models.WhatsAppTemplate.id == broadcast_request.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Get customers
        customers = []
        if broadcast_request.customer_ids:
            customers = db.query(models.Customer).filter(models.Customer.id.in_(broadcast_request.customer_ids)).all()
        else:
            # Get top 50 customers by spending
            customers = db.query(models.Customer).order_by(models.Customer.total_spent.desc()).limit(50).all()
        
        if not customers:
            raise HTTPException(status_code=400, detail="No customers found for broadcast")
        
        results = []
        for customer in customers:
            # Format message with customer variables
            message = broadcast_request.message.format(
                customer_name=customer.name or "Valued Customer",
                customer_phone=customer.phone,
                total_spent=customer.total_spent,
                loyalty_points=customer.loyalty_points,
                total_orders=customer.total_orders
            )
            
            # Send message
            result = whatsapp_service.send_text_message(customer.phone, message)
            
            # Log the message
            log_entry = models.WhatsAppLog(
                customer_id=customer.id,
                phone_number=customer.phone,
                template_id=template.id,
                message_type="BROADCAST",
                message_content=message,
                status=result["status"],
                interakt_message_id=result.get("message_id"),
                error_message=result.get("error")
            )
            db.add(log_entry)
            
            results.append({
                "customer_id": customer.id,
                "phone": customer.phone,
                "success": result["success"],
                "status": result["status"]
            })
        
        db.commit()
        
        return {
            "total_sent": len(results),
            "successful": len([r for r in results if r["success"]]),
            "failed": len([r for r in results if not r["success"]]),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending broadcast: {str(e)}")

@app.get("/whatsapp/logs/", response_model=List[schemas.WhatsAppLog])
def get_whatsapp_logs(
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = None,
    message_type: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get WhatsApp message logs"""
    try:
        query = db.query(models.WhatsAppLog)
        
        if customer_id:
            query = query.filter(models.WhatsAppLog.customer_id == customer_id)
        
        if message_type:
            query = query.filter(models.WhatsAppLog.message_type == message_type)
        
        logs = query.order_by(models.WhatsAppLog.sent_at.desc()).offset(skip).limit(limit).all()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching WhatsApp logs: {str(e)}")

@app.get("/whatsapp/logs/{log_id}", response_model=schemas.WhatsAppLog)
def get_whatsapp_log(
    log_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get a specific WhatsApp log entry"""
    try:
        log = db.query(models.WhatsAppLog).filter(models.WhatsAppLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log entry not found")
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching log: {str(e)}")

# ==================== RBAC ENDPOINTS ====================

@app.post("/rbac/initialize")
def initialize_rbac(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Initialize RBAC system with default permissions"""
    try:
        rbac_service.initialize_permissions(db)
        return {"message": "RBAC system initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing RBAC: {str(e)}")

@app.get("/rbac/permissions", response_model=List[schemas.Permission])
def get_all_permissions(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get all available permissions"""
    try:
        return rbac_service.get_all_permissions(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching permissions: {str(e)}")

@app.get("/rbac/roles/{role}/permissions", response_model=List[schemas.Permission])
def get_role_permissions(
    role: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get permissions for a specific role"""
    try:
        user_role = models.UserRole(role)
        return rbac_service.get_role_permissions(db, user_role)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching role permissions: {str(e)}")

@app.post("/rbac/roles/{role}/permissions")
def assign_permissions_to_role(
    role: str,
    assignment: schemas.PermissionAssignment,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Assign permissions to a role"""
    try:
        user_role = models.UserRole(role)
        success = rbac_service.assign_permissions_to_role(db, user_role, assignment.permissions)
        if success:
            return {"message": f"Permissions assigned to role {role} successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to assign permissions")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning permissions: {str(e)}")

@app.post("/rbac/users/{user_id}/permissions")
def assign_permissions_to_user(
    user_id: int,
    assignment: schemas.UserPermissionAssignment,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Assign permissions to a user"""
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        success = rbac_service.assign_permissions_to_user(db, user_id, assignment.permissions, assignment.is_granted)
        if success:
            return {"message": f"Permissions assigned to user {user_id} successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to assign permissions")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning permissions: {str(e)}")

@app.get("/rbac/users/{user_id}/permissions")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get all permissions for a specific user"""
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        permissions = rbac_service.get_user_permissions(db, user_id)
        return {"user_id": user_id, "permissions": list(permissions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user permissions: {str(e)}")

@app.get("/rbac/roles/summary")
def get_role_summary(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Get summary of all roles with their permissions and user counts"""
    try:
        return rbac_service.get_role_summary(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching role summary: {str(e)}")

@app.put("/rbac/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    """Update user's role"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.role = role_update.role
        db.commit()
        db.refresh(user)
        
        return {"message": f"User role updated to {role_update.role.value} successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user role: {str(e)}")

@app.get("/rbac/check-permission/{permission_name}")
def check_user_permission(
    permission_name: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Check if current user has a specific permission"""
    try:
        has_perm = rbac_service.has_permission(db, current_user.id, permission_name)
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "permission": permission_name,
            "has_permission": has_perm
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking permission: {str(e)}")

@app.get("/rbac/check-resource-permission/{resource}/{action}")
def check_resource_permission(
    resource: str,
    action: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Check if current user has permission for a specific resource and action"""
    try:
        has_perm = rbac_service.has_resource_permission(db, current_user.id, resource, action)
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "resource": resource,
            "action": action,
            "has_permission": has_perm
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking resource permission: {str(e)}")

# ==================== CONFIGURATION ENDPOINTS ====================

@app.get("/config/whatsapp")
def get_whatsapp_config(
    current_user: models.User = Depends(auth.require_admin)
):
    """Get WhatsApp configuration status"""
    try:
        config = settings.get_whatsapp_config()
        return {
            "configured": settings.is_whatsapp_configured(),
            "enabled": config["enabled"],
            "has_api_key": bool(config["api_key"]),
            "has_api_secret": bool(config["api_secret"]),
            "has_phone_number_id": bool(config["phone_number_id"]),
            "has_business_account_id": bool(config["business_account_id"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting WhatsApp config: {str(e)}")

@app.post("/config/whatsapp")
def update_whatsapp_config(
    api_key: str,
    api_secret: str,
    phone_number_id: str,
    business_account_id: str,
    current_user: models.User = Depends(auth.require_admin)
):
    """Update WhatsApp configuration"""
    try:
        # In a production environment, you would save these to environment variables
        # or a secure configuration file
        settings.INTERAKT_API_KEY = api_key
        settings.INTERAKT_API_SECRET = api_secret
        settings.INTERAKT_PHONE_NUMBER_ID = phone_number_id
        settings.INTERAKT_BUSINESS_ACCOUNT_ID = business_account_id
        settings.WHATSAPP_ENABLED = bool(api_key and api_secret)
        
        return {
            "message": "WhatsApp configuration updated successfully",
            "configured": settings.is_whatsapp_configured(),
            "enabled": settings.WHATSAPP_ENABLED
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating WhatsApp config: {str(e)}")

@app.get("/config/shop")
def get_shop_config(
    current_user: models.User = Depends(auth.require_admin)
):
    """Get shop configuration"""
    try:
        return {
            "shop_name": settings.SHOP_NAME,
            "shop_address": settings.SHOP_ADDRESS,
            "shop_phone": settings.SHOP_PHONE,
            "shop_email": settings.SHOP_EMAIL,
            "shop_gstin": settings.SHOP_GSTIN
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting shop config: {str(e)}")

@app.post("/config/shop")
def update_shop_config(
    shop_name: str,
    shop_address: str,
    shop_phone: str,
    shop_email: str,
    shop_gstin: str,
    current_user: models.User = Depends(auth.require_admin)
):
    """Update shop configuration"""
    try:
        settings.SHOP_NAME = shop_name
        settings.SHOP_ADDRESS = shop_address
        settings.SHOP_PHONE = shop_phone
        settings.SHOP_EMAIL = shop_email
        settings.SHOP_GSTIN = shop_gstin
        
        return {
            "message": "Shop configuration updated successfully",
            "shop_name": settings.SHOP_NAME,
            "shop_address": settings.SHOP_ADDRESS,
            "shop_phone": settings.SHOP_PHONE,
            "shop_email": settings.SHOP_EMAIL,
            "shop_gstin": settings.SHOP_GSTIN
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating shop config: {str(e)}")

# ==================== ERROR HANDLER SETUP ====================
# Setup comprehensive error handling
setup_error_handlers(app)

# Log application startup
logger.info("Garments POS System API started successfully")
logger.info("Error handling system initialized") 