from pydantic import BaseModel
from typing import List, Optional
import datetime
from models import UserRole

# Dealer Schemas
class DealerBase(BaseModel):
    name: str
    pan: str
    gst: str
    address: Optional[str] = None

class DealerCreate(DealerBase):
    pass

class Dealer(DealerBase):
    id: int
    
    class Config:
        orm_mode = True

# Brand Schemas
class BrandBase(BaseModel):
    name: str

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    description: Optional[str] = None
    
    class Config:
        orm_mode = True

# Product Schemas
class ProductBase(BaseModel):
    brand_id: int
    type: str
    size_type: str = "ALPHA"
    gst_rate: float = 12.0

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    name: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True

# Inventory Item Schemas
class InventoryItemBase(BaseModel):
    product_id: int
    barcode: str
    design_number: str  # Moved from Product
    size: str  # Actual size value (XS, S, M, L, XL, etc.)
    color: str
    cost_price: float  # Moved from Product
    mrp: float  # Moved from Product
    quantity: int = 1 # Default to 1 for individual items

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemSubtract(BaseModel):
    barcode: str
    quantity: int

class InventoryItem(InventoryItemBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    product: Optional[schemas.Product] = None
    
    class Config:
        orm_mode = True

# Inventory Summary Schema
class InventorySummary(BaseModel):
    product_id: int
    product_name: str
    brand_name: str
    total_quantity: int
    inventory_items: List[InventoryItem]
    
    class Config:
        orm_mode = True 

# Invoice Schemas
class InvoiceItemBase(BaseModel):
    inventory_item_id: int
    barcode: str
    product_name: str
    design_number: str
    size: str
    color: str
    unit_price: float  # MRP (GST-inclusive)
    quantity: int = 1
    total_price: float  # Total MRP for this item
    discount_amount: float = 0  # Discount applied to this item
    final_price: float  # Final price after discount (GST-inclusive)
    base_price: float  # Price excluding GST
    gst_amount: float  # Total GST amount
    cgst_amount: float  # CGST amount
    sgst_amount: float  # SGST amount
    gst_rate: float  # GST rate for this item

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    invoice_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class InvoiceBase(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    total_mrp: float  # Total MRP before discount
    total_discount: float  # Total discount applied
    total_final_price: float  # Total final price after discount
    total_base_amount: float  # Total base amount (ex-GST)
    total_gst_amount: float  # Total GST amount
    total_cgst_amount: float  # Total CGST amount
    total_sgst_amount: float  # Total SGST amount
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]

class Invoice(InvoiceBase):
    id: int
    invoice_number: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    items: List[InvoiceItem]
    class Config:
        orm_mode = True

# Checkout Schemas
class CheckoutItem(BaseModel):
    barcode: str
    quantity: int = 1

class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    discount_type: Optional[str] = None  # PERCENT or FIXED
    discount_value: float = 0
    loyalty_points_redeemed: int = 0  # Points to redeem for discount
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class CheckoutResponse(BaseModel):
    invoice: Invoice
    message: str 

class ReturnItemBase(BaseModel):
    invoice_item_id: int
    inventory_item_id: int
    barcode: str
    product_name: str
    design_number: str
    size: str
    color: str
    original_quantity: int
    return_quantity: int
    unit_price: float
    total_return_price: float  # Negative amount
    return_gst_amount: float  # Negative GST amount
    return_cgst_amount: float  # Negative CGST amount
    return_sgst_amount: float  # Negative SGST amount
    gst_rate: float

class ReturnItemCreate(ReturnItemBase):
    pass

class ReturnItem(ReturnItemBase):
    id: int
    return_id: int
    created_at: datetime.datetime
    class Config:
        orm_mode = True

class ReturnBase(BaseModel):
    invoice_id: int
    invoice_number: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    return_reason: Optional[str] = None
    return_method: str = "CASH"
    total_return_amount: float  # Negative amount
    total_return_gst: float  # Negative GST amount
    total_return_cgst: float  # Negative CGST amount
    total_return_sgst: float  # Negative SGST amount
    wallet_credit: float = 0
    cash_refund: float = 0
    notes: Optional[str] = None

class ReturnCreate(ReturnBase):
    items: List[ReturnItemCreate]

class Return(ReturnBase):
    id: int
    return_number: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    items: List[ReturnItem]
    class Config:
        orm_mode = True

# Return Request Schemas
class ReturnItemRequest(BaseModel):
    invoice_item_id: int
    return_quantity: int

class ReturnRequest(BaseModel):
    invoice_number: str
    items: List[ReturnItemRequest]
    return_reason: Optional[str] = None
    return_method: str = "CASH"  # CASH, WALLET, STORE_CREDIT
    wallet_credit: Optional[float] = None  # Auto-calculated based on return method
    cash_refund: Optional[float] = None    # Auto-calculated based on return method
    notes: Optional[str] = None

class ReturnResponse(BaseModel):
    return_record: Return
    message: str

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole = UserRole.CASHIER

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# Cash Register Schemas
class CashExpenseBase(BaseModel):
    category: str
    description: str
    amount: float

class CashExpenseCreate(CashExpenseBase):
    pass

class CashExpense(CashExpenseBase):
    id: int
    cash_register_id: int
    date: datetime.datetime
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class CashRegisterBase(BaseModel):
    opening_balance: float
    notes: Optional[str] = None

class CashRegisterCreate(CashRegisterBase):
    pass

class CashRegister(CashRegisterBase):
    id: int
    date: datetime.datetime
    closing_balance: float
    total_sales: float
    total_returns: float
    total_expenses: float
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    expenses: List[CashExpense]
    
    class Config:
        orm_mode = True

class CashRegisterSummary(BaseModel):
    date: str
    opening_balance: float
    closing_balance: float
    total_sales: float
    total_returns: float
    total_expenses: float
    net_cash: float
    expenses: List[CashExpense]

# CRM & Loyalty System Schemas
class CustomerBase(BaseModel):
    phone: str
    name: Optional[str] = None  # Made optional for CRM
    email: Optional[str] = None
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    loyalty_points: int
    total_spent: float
    total_orders: int
    last_visit_date: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True

class LoyaltyTransactionBase(BaseModel):
    transaction_type: str  # EARNED, REDEEMED, ADJUSTED
    points: int
    amount_spent: Optional[float] = None
    discount_amount: Optional[float] = None
    description: str

class LoyaltyTransactionCreate(LoyaltyTransactionBase):
    customer_id: int
    invoice_id: Optional[int] = None

class LoyaltyTransaction(LoyaltyTransactionBase):
    id: int
    customer_id: int
    invoice_id: Optional[int] = None
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class CustomerLoyaltyInfo(BaseModel):
    customer: Customer
    loyalty_points: int
    total_spent: float
    total_orders: int
    recent_transactions: List[LoyaltyTransaction]

class LoyaltyRedemptionRequest(BaseModel):
    customer_phone: str
    points_to_redeem: int

class LoyaltyRedemptionResponse(BaseModel):
    customer: Customer
    points_redeemed: int
    discount_amount: float
    remaining_points: int

# CRM Schemas
class CustomerSearchRequest(BaseModel):
    search_term: str  # Can be name or phone

class CustomerSearchResponse(BaseModel):
    customers: List[Customer]
    total_count: int

class CustomerVisitHistory(BaseModel):
    customer: Customer
    invoices: List[Invoice]
    total_visits: int
    total_spent: float
    average_order_value: float
    last_visit_date: Optional[datetime.datetime] = None

class CustomerExportRequest(BaseModel):
    include_phone: bool = True
    include_email: bool = True
    include_address: bool = True
    include_loyalty: bool = True
    include_visit_history: bool = True

# WhatsApp Messaging Schemas
class WhatsAppTemplateBase(BaseModel):
    name: str
    template_type: str
    message_template: str
    variables: Optional[str] = None
    is_active: bool = True

class WhatsAppTemplateCreate(WhatsAppTemplateBase):
    pass

class WhatsAppTemplate(WhatsAppTemplateBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True

class WhatsAppLogBase(BaseModel):
    phone_number: str
    message_type: str
    message_content: str
    status: str
    interakt_message_id: Optional[str] = None
    error_message: Optional[str] = None

class WhatsAppLogCreate(WhatsAppLogBase):
    customer_id: Optional[int] = None
    invoice_id: Optional[int] = None
    template_id: Optional[int] = None

class WhatsAppLog(WhatsAppLogBase):
    id: int
    customer_id: Optional[int] = None
    invoice_id: Optional[int] = None
    template_id: Optional[int] = None
    sent_at: datetime.datetime
    
    class Config:
        orm_mode = True

class WhatsAppBroadcastRequest(BaseModel):
    template_id: int
    customer_ids: List[int] = []
    message: str
    include_pdf: bool = False

class WhatsAppConfig(BaseModel):
    api_key: str
    api_secret: str
    phone_number_id: str
    business_account_id: str

# ==================== RBAC SCHEMAS ====================

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True

class RolePermissionBase(BaseModel):
    role: UserRole
    permission_id: int
    is_active: bool = True

class RolePermissionCreate(RolePermissionBase):
    pass

class RolePermission(RolePermissionBase):
    id: int
    permission: Permission
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True

class UserPermissionBase(BaseModel):
    user_id: int
    permission_id: int
    is_granted: bool = True
    is_active: bool = True

class UserPermissionCreate(UserPermissionBase):
    pass

class UserPermission(UserPermissionBase):
    id: int
    permission: Permission
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    
    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime] = None
    permissions: List[RolePermission] = []
    
    class Config:
        orm_mode = True

class UserRoleUpdate(BaseModel):
    role: UserRole

class PermissionAssignment(BaseModel):
    role: UserRole
    permissions: List[int]  # List of permission IDs

class UserPermissionAssignment(BaseModel):
    user_id: int
    permissions: List[int]  # List of permission IDs
    is_granted: bool = True

class RoleSummary(BaseModel):
    role: UserRole
    total_users: int
    total_permissions: int
    is_active: bool

class PermissionSummary(BaseModel):
    permission: Permission
    total_roles: int
    total_users: int
    is_active: bool 