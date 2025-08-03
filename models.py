from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    CASHIER = "cashier"
    INVENTORY_MANAGER = "inventory_manager"
    MANAGER = "manager"  # New role for general management
    VIEWER = "viewer"    # New role for read-only access

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CASHIER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Dealer(Base):
    __tablename__ = "dealers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    pan = Column(String, nullable=False)  # PAN number
    gst = Column(String, nullable=False)  # GST number
    address = Column(String, nullable=True)  # Optional address
    
    # Relationship with brands (many-to-many through association table)
    brands = relationship("Brand", secondary="dealer_brands", back_populates="dealers")

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    products = relationship("Product", back_populates="brand")
    dealers = relationship("Dealer", secondary="dealer_brands", back_populates="brands")

# Association table for many-to-many relationship between dealers and brands
class DealerBrand(Base):
    __tablename__ = "dealer_brands"
    
    dealer_id = Column(Integer, ForeignKey("dealers.id"), primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), primary_key=True)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Auto-generated: Brand-Type
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    type = Column(String, nullable=False)
    size_type = Column(String, nullable=False, default="ALPHA")  # ALPHA, NUMERIC, or CUSTOM
    gst_rate = Column(Float, nullable=False, default=12.0)  # GST rate for this product (default 12%)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    brand = relationship("Brand", back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    barcode = Column(String, unique=True, nullable=False, index=True)
    design_number = Column(String, nullable=False)  # Moved from Product
    size = Column(String, nullable=False)  # Actual size value (XS, S, M, L, XL, etc.)
    color = Column(String, nullable=False)
    cost_price = Column(Float, nullable=False)  # Moved from Product
    mrp = Column(Float, nullable=False)  # Moved from Product
    quantity = Column(Integer, nullable=False, default=0) # This is now always 1 for individual items
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    product = relationship("Product", back_populates="inventory_items")
    __table_args__ = (
        UniqueConstraint('barcode', name='uq_inventory_barcode'),
    )

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    total_mrp = Column(Float, nullable=False)  # Total MRP before discount
    total_discount = Column(Float, nullable=False, default=0)  # Total discount applied
    total_final_price = Column(Float, nullable=False)  # Total final price after discount
    total_base_amount = Column(Float, nullable=False)  # Total base amount (ex-GST)
    total_gst_amount = Column(Float, nullable=False)  # Total GST amount
    total_cgst_amount = Column(Float, nullable=False)  # Total CGST amount
    total_sgst_amount = Column(Float, nullable=False)  # Total SGST amount
    payment_method = Column(String, nullable=True)  # CASH, CARD, UPI, etc.
    loyalty_points_earned = Column(Integer, default=0, nullable=False)
    loyalty_points_redeemed = Column(Integer, default=0, nullable=False)
    loyalty_discount_amount = Column(Float, default=0.0, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    items = relationship("InvoiceItem", back_populates="invoice")
    returns = relationship("Return", back_populates="invoice")
    customer = relationship("Customer", back_populates="invoices")
    loyalty_transactions = relationship("LoyaltyTransaction", back_populates="invoice")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    barcode = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    design_number = Column(String, nullable=False)
    size = Column(String, nullable=False)
    color = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)  # MRP (GST-inclusive)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Float, nullable=False)  # Total MRP for this item
    discount_amount = Column(Float, nullable=False, default=0)  # Discount applied to this item
    final_price = Column(Float, nullable=False)  # Final price after discount (GST-inclusive)
    base_price = Column(Float, nullable=False)  # Price excluding GST
    gst_amount = Column(Float, nullable=False)  # Total GST amount
    cgst_amount = Column(Float, nullable=False)  # CGST amount
    sgst_amount = Column(Float, nullable=False)  # SGST amount
    gst_rate = Column(Float, nullable=False)  # GST rate for this item
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    invoice = relationship("Invoice", back_populates="items")
    inventory_item = relationship("InventoryItem") 

class Return(Base):
    __tablename__ = "returns"
    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String, unique=True, nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    invoice_number = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    return_reason = Column(Text, nullable=True)
    return_method = Column(String, nullable=False, default="CASH")  # CASH, WALLET, STORE_CREDIT
    total_return_amount = Column(Float, nullable=False)  # Negative amount
    total_return_gst = Column(Float, nullable=False)  # Negative GST amount
    total_return_cgst = Column(Float, nullable=False)  # Negative CGST amount
    total_return_sgst = Column(Float, nullable=False)  # Negative SGST amount
    wallet_credit = Column(Float, nullable=False, default=0)  # Amount credited to wallet
    cash_refund = Column(Float, nullable=False, default=0)  # Cash refund amount
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    invoice = relationship("Invoice", back_populates="returns")
    items = relationship("ReturnItem", back_populates="return_record")

class ReturnItem(Base):
    __tablename__ = "return_items"
    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)
    invoice_item_id = Column(Integer, ForeignKey("invoice_items.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    barcode = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    design_number = Column(String, nullable=False)
    size = Column(String, nullable=False)
    color = Column(String, nullable=False)
    original_quantity = Column(Integer, nullable=False)  # Quantity from original invoice
    return_quantity = Column(Integer, nullable=False)  # Quantity being returned
    unit_price = Column(Float, nullable=False)  # Original unit price
    total_return_price = Column(Float, nullable=False)  # Negative amount
    return_gst_amount = Column(Float, nullable=False)  # Negative GST amount
    return_cgst_amount = Column(Float, nullable=False)  # Negative CGST amount
    return_sgst_amount = Column(Float, nullable=False)  # Negative SGST amount
    gst_rate = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    return_record = relationship("Return", back_populates="items")
    invoice_item = relationship("InvoiceItem")
    inventory_item = relationship("InventoryItem")

class CashRegister(Base):
    __tablename__ = "cash_register"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    opening_balance = Column(Float, nullable=False, default=0.0)
    closing_balance = Column(Float, nullable=False, default=0.0)
    total_sales = Column(Float, nullable=False, default=0.0)
    total_returns = Column(Float, nullable=False, default=0.0)
    total_expenses = Column(Float, nullable=False, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    expenses = relationship("CashExpense", back_populates="cash_register")

class CashExpense(Base):
    __tablename__ = "cash_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    cash_register_id = Column(Integer, ForeignKey("cash_register.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    category = Column(String, nullable=False)  # e.g., "Courier", "Packaging", "Lunch", "Other"
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    cash_register = relationship("CashRegister", back_populates="expenses")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)  # Made optional for CRM
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    loyalty_points = Column(Integer, default=0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)
    total_orders = Column(Integer, default=0, nullable=False)
    last_visit_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoices = relationship("Invoice", back_populates="customer")
    loyalty_transactions = relationship("LoyaltyTransaction", back_populates="customer")

class LoyaltyTransaction(Base):
    __tablename__ = "loyalty_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)  # Null for manual adjustments
    transaction_type = Column(String, nullable=False)  # EARNED, REDEEMED, ADJUSTED
    points = Column(Integer, nullable=False)  # Positive for earned, negative for redeemed
    amount_spent = Column(Float, nullable=True)  # Amount that earned points
    discount_amount = Column(Float, nullable=True)  # Amount discounted by points
    description = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="loyalty_transactions")
    invoice = relationship("Invoice", back_populates="loyalty_transactions")

# WhatsApp Messaging Models
class WhatsAppTemplate(Base):
    __tablename__ = "whatsapp_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    template_type = Column(String, nullable=False)  # INVOICE, THANK_YOU, BROADCAST, CUSTOM
    message_template = Column(Text, nullable=False)
    variables = Column(Text, nullable=True)  # JSON string of available variables
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class WhatsAppLog(Base):
    __tablename__ = "whatsapp_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("whatsapp_templates.id"), nullable=True)
    phone_number = Column(String, nullable=False)
    message_type = Column(String, nullable=False)  # INVOICE, THANK_YOU, BROADCAST, CUSTOM
    message_content = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # SENT, DELIVERED, FAILED, PENDING
    interakt_message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer")
    invoice = relationship("Invoice")
    template = relationship("WhatsAppTemplate")

# ==================== RBAC MODELS ====================

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)  # e.g., "read_invoices", "create_products"
    description = Column(String, nullable=True)
    resource = Column(String, nullable=False)  # e.g., "invoices", "products", "inventory"
    action = Column(String, nullable=False)    # e.g., "read", "create", "update", "delete"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(Enum(UserRole), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    permission = relationship("Permission")

class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    is_granted = Column(Boolean, default=True, nullable=False)  # True for grant, False for deny
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    permission = relationship("Permission")

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships - Note: RolePermission doesn't have a foreign key to Role
    # The role is stored as an enum in the RolePermission table itself

# Remove the problematic relationship line since RolePermission doesn't have a foreign key to Role
# The role is stored as an enum in the RolePermission table itself