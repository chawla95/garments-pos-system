"""
Role-Based Access Control (RBAC) Service
Handles permission checking and role management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Optional, Set
import models
from models import UserRole

class RBACService:
    def __init__(self):
        # Define default permissions for each role
        self.default_permissions = {
            UserRole.ADMIN: [
                # Full access to everything
                "read_invoices", "create_invoices", "update_invoices", "delete_invoices",
                "read_products", "create_products", "update_products", "delete_products",
                "read_inventory", "create_inventory", "update_inventory", "delete_inventory",
                "read_dealers", "create_dealers", "update_dealers", "delete_dealers",
                "read_brands", "create_brands", "update_brands", "delete_brands",
                "read_returns", "create_returns", "update_returns", "delete_returns",
                "read_cash_register", "create_cash_register", "update_cash_register", "delete_cash_register",
                "read_customers", "create_customers", "update_customers", "delete_customers",
                "read_loyalty", "create_loyalty", "update_loyalty", "delete_loyalty",
                "read_crm", "create_crm", "update_crm", "delete_crm",
                "read_whatsapp", "create_whatsapp", "update_whatsapp", "delete_whatsapp",
                "read_ml", "create_ml", "update_ml", "delete_ml",
                "read_users", "create_users", "update_users", "delete_users",
                "read_permissions", "create_permissions", "update_permissions", "delete_permissions",
                "read_roles", "create_roles", "update_roles", "delete_roles",
                "read_dashboard", "read_reports", "export_data"
            ],
            UserRole.CASHIER: [
                # Cashier can handle sales and basic operations
                "read_invoices", "create_invoices", "read_products", "read_inventory",
                "read_returns", "create_returns", "read_cash_register", "create_cash_register",
                "read_customers", "create_customers", "update_customers", "read_loyalty",
                "create_loyalty", "read_crm", "read_whatsapp", "read_dashboard"
            ],
            UserRole.INVENTORY_MANAGER: [
                # Inventory manager can handle inventory and products
                "read_products", "create_products", "update_products", "read_inventory",
                "create_inventory", "update_inventory", "delete_inventory", "read_dealers",
                "read_brands", "read_dashboard", "read_reports"
            ],
            UserRole.MANAGER: [
                # Manager has broad access but not admin privileges
                "read_invoices", "create_invoices", "read_products", "create_products", "update_products",
                "read_inventory", "create_inventory", "update_inventory", "read_dealers", "create_dealers",
                "read_brands", "create_brands", "read_returns", "create_returns", "read_cash_register",
                "read_customers", "create_customers", "update_customers", "read_loyalty", "create_loyalty",
                "read_crm", "read_whatsapp", "read_dashboard", "read_reports", "export_data"
            ],
            UserRole.VIEWER: [
                # Viewer has read-only access to most features
                "read_invoices", "read_products", "read_inventory", "read_dealers", "read_brands",
                "read_returns", "read_cash_register", "read_customers", "read_loyalty", "read_crm",
                "read_dashboard", "read_reports"
            ]
        }
    
    def initialize_permissions(self, db: Session):
        """Initialize default permissions in the database"""
        # Create permissions if they don't exist
        permissions_data = [
            # Invoice permissions
            {"name": "read_invoices", "description": "View invoices", "resource": "invoices", "action": "read"},
            {"name": "create_invoices", "description": "Create invoices", "resource": "invoices", "action": "create"},
            {"name": "update_invoices", "description": "Update invoices", "resource": "invoices", "action": "update"},
            {"name": "delete_invoices", "description": "Delete invoices", "resource": "invoices", "action": "delete"},
            
            # Product permissions
            {"name": "read_products", "description": "View products", "resource": "products", "action": "read"},
            {"name": "create_products", "description": "Create products", "resource": "products", "action": "create"},
            {"name": "update_products", "description": "Update products", "resource": "products", "action": "update"},
            {"name": "delete_products", "description": "Delete products", "resource": "products", "action": "delete"},
            
            # Inventory permissions
            {"name": "read_inventory", "description": "View inventory", "resource": "inventory", "action": "read"},
            {"name": "create_inventory", "description": "Create inventory items", "resource": "inventory", "action": "create"},
            {"name": "update_inventory", "description": "Update inventory", "resource": "inventory", "action": "update"},
            {"name": "delete_inventory", "description": "Delete inventory", "resource": "inventory", "action": "delete"},
            
            # Dealer permissions
            {"name": "read_dealers", "description": "View dealers", "resource": "dealers", "action": "read"},
            {"name": "create_dealers", "description": "Create dealers", "resource": "dealers", "action": "create"},
            {"name": "update_dealers", "description": "Update dealers", "resource": "dealers", "action": "update"},
            {"name": "delete_dealers", "description": "Delete dealers", "resource": "dealers", "action": "delete"},
            
            # Brand permissions
            {"name": "read_brands", "description": "View brands", "resource": "brands", "action": "read"},
            {"name": "create_brands", "description": "Create brands", "resource": "brands", "action": "create"},
            {"name": "update_brands", "description": "Update brands", "resource": "brands", "action": "update"},
            {"name": "delete_brands", "description": "Delete brands", "resource": "brands", "action": "delete"},
            
            # Return permissions
            {"name": "read_returns", "description": "View returns", "resource": "returns", "action": "read"},
            {"name": "create_returns", "description": "Create returns", "resource": "returns", "action": "create"},
            {"name": "update_returns", "description": "Update returns", "resource": "returns", "action": "update"},
            {"name": "delete_returns", "description": "Delete returns", "resource": "returns", "action": "delete"},
            
            # Cash Register permissions
            {"name": "read_cash_register", "description": "View cash register", "resource": "cash_register", "action": "read"},
            {"name": "create_cash_register", "description": "Create cash register entries", "resource": "cash_register", "action": "create"},
            {"name": "update_cash_register", "description": "Update cash register", "resource": "cash_register", "action": "update"},
            {"name": "delete_cash_register", "description": "Delete cash register entries", "resource": "cash_register", "action": "delete"},
            
            # Customer permissions
            {"name": "read_customers", "description": "View customers", "resource": "customers", "action": "read"},
            {"name": "create_customers", "description": "Create customers", "resource": "customers", "action": "create"},
            {"name": "update_customers", "description": "Update customers", "resource": "customers", "action": "update"},
            {"name": "delete_customers", "description": "Delete customers", "resource": "customers", "action": "delete"},
            
            # Loyalty permissions
            {"name": "read_loyalty", "description": "View loyalty", "resource": "loyalty", "action": "read"},
            {"name": "create_loyalty", "description": "Create loyalty transactions", "resource": "loyalty", "action": "create"},
            {"name": "update_loyalty", "description": "Update loyalty", "resource": "loyalty", "action": "update"},
            {"name": "delete_loyalty", "description": "Delete loyalty", "resource": "loyalty", "action": "delete"},
            
            # CRM permissions
            {"name": "read_crm", "description": "View CRM", "resource": "crm", "action": "read"},
            {"name": "create_crm", "description": "Create CRM entries", "resource": "crm", "action": "create"},
            {"name": "update_crm", "description": "Update CRM", "resource": "crm", "action": "update"},
            {"name": "delete_crm", "description": "Delete CRM", "resource": "crm", "action": "delete"},
            
            # WhatsApp permissions
            {"name": "read_whatsapp", "description": "View WhatsApp", "resource": "whatsapp", "action": "read"},
            {"name": "create_whatsapp", "description": "Create WhatsApp messages", "resource": "whatsapp", "action": "create"},
            {"name": "update_whatsapp", "description": "Update WhatsApp", "resource": "whatsapp", "action": "update"},
            {"name": "delete_whatsapp", "description": "Delete WhatsApp", "resource": "whatsapp", "action": "delete"},
            
            # ML permissions
            {"name": "read_ml", "description": "View ML analytics", "resource": "ml", "action": "read"},
            {"name": "create_ml", "description": "Create ML models", "resource": "ml", "action": "create"},
            {"name": "update_ml", "description": "Update ML", "resource": "ml", "action": "update"},
            {"name": "delete_ml", "description": "Delete ML", "resource": "ml", "action": "delete"},
            
            # User management permissions
            {"name": "read_users", "description": "View users", "resource": "users", "action": "read"},
            {"name": "create_users", "description": "Create users", "resource": "users", "action": "create"},
            {"name": "update_users", "description": "Update users", "resource": "users", "action": "update"},
            {"name": "delete_users", "description": "Delete users", "resource": "users", "action": "delete"},
            
            # Permission management
            {"name": "read_permissions", "description": "View permissions", "resource": "permissions", "action": "read"},
            {"name": "create_permissions", "description": "Create permissions", "resource": "permissions", "action": "create"},
            {"name": "update_permissions", "description": "Update permissions", "resource": "permissions", "action": "update"},
            {"name": "delete_permissions", "description": "Delete permissions", "resource": "permissions", "action": "delete"},
            
            # Role management
            {"name": "read_roles", "description": "View roles", "resource": "roles", "action": "read"},
            {"name": "create_roles", "description": "Create roles", "resource": "roles", "action": "create"},
            {"name": "update_roles", "description": "Update roles", "resource": "roles", "action": "update"},
            {"name": "delete_roles", "description": "Delete roles", "resource": "roles", "action": "delete"},
            
            # General permissions
            {"name": "read_dashboard", "description": "View dashboard", "resource": "dashboard", "action": "read"},
            {"name": "read_reports", "description": "View reports", "resource": "reports", "action": "read"},
            {"name": "export_data", "description": "Export data", "resource": "data", "action": "export"}
        ]
        
        for perm_data in permissions_data:
            existing = db.query(models.Permission).filter(models.Permission.name == perm_data["name"]).first()
            if not existing:
                permission = models.Permission(**perm_data)
                db.add(permission)
        
        db.commit()
        
        # Assign default permissions to roles
        for role, permissions in self.default_permissions.items():
            for perm_name in permissions:
                permission = db.query(models.Permission).filter(models.Permission.name == perm_name).first()
                if permission:
                    existing_role_perm = db.query(models.RolePermission).filter(
                        and_(
                            models.RolePermission.role == role,
                            models.RolePermission.permission_id == permission.id
                        )
                    ).first()
                    
                    if not existing_role_perm:
                        role_permission = models.RolePermission(
                            role=role,
                            permission_id=permission.id,
                            is_active=True
                        )
                        db.add(role_permission)
        
        db.commit()
    
    def get_user_permissions(self, db: Session, user_id: int) -> Set[str]:
        """Get all permissions for a user (role-based + individual permissions)"""
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return set()
        
        permissions = set()
        
        # Get role-based permissions
        role_permissions = db.query(models.RolePermission).filter(
            and_(
                models.RolePermission.role == user.role,
                models.RolePermission.is_active == True
            )
        ).all()
        
        for role_perm in role_permissions:
            permission = db.query(models.Permission).filter(models.Permission.id == role_perm.permission_id).first()
            if permission:
                permissions.add(permission.name)
        
        # Get individual user permissions
        user_permissions = db.query(models.UserPermission).filter(
            and_(
                models.UserPermission.user_id == user_id,
                models.UserPermission.is_active == True
            )
        ).all()
        
        for user_perm in user_permissions:
            permission = db.query(models.Permission).filter(models.Permission.id == user_perm.permission_id).first()
            if permission:
                if user_perm.is_granted:
                    permissions.add(permission.name)
                else:
                    permissions.discard(permission.name)  # Remove if denied
        
        return permissions
    
    def has_permission(self, db: Session, user_id: int, permission_name: str) -> bool:
        """Check if a user has a specific permission"""
        user_permissions = self.get_user_permissions(db, user_id)
        return permission_name in user_permissions
    
    def has_resource_permission(self, db: Session, user_id: int, resource: str, action: str) -> bool:
        """Check if a user has permission for a specific resource and action"""
        permission_name = f"{action}_{resource}"
        return self.has_permission(db, user_id, permission_name)
    
    def get_role_permissions(self, db: Session, role: UserRole) -> List[models.Permission]:
        """Get all permissions for a specific role"""
        role_permissions = db.query(models.RolePermission).filter(
            and_(
                models.RolePermission.role == role,
                models.RolePermission.is_active == True
            )
        ).all()
        
        permissions = []
        for role_perm in role_permissions:
            permission = db.query(models.Permission).filter(models.Permission.id == role_perm.permission_id).first()
            if permission:
                permissions.append(permission)
        
        return permissions
    
    def assign_permissions_to_role(self, db: Session, role: UserRole, permission_ids: List[int]) -> bool:
        """Assign permissions to a role"""
        try:
            # Remove existing permissions for this role
            db.query(models.RolePermission).filter(models.RolePermission.role == role).delete()
            
            # Add new permissions
            for permission_id in permission_ids:
                role_permission = models.RolePermission(
                    role=role,
                    permission_id=permission_id,
                    is_active=True
                )
                db.add(role_permission)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
    
    def assign_permissions_to_user(self, db: Session, user_id: int, permission_ids: List[int], is_granted: bool = True) -> bool:
        """Assign permissions to a user"""
        try:
            # Remove existing individual permissions for this user
            db.query(models.UserPermission).filter(models.UserPermission.user_id == user_id).delete()
            
            # Add new permissions
            for permission_id in permission_ids:
                user_permission = models.UserPermission(
                    user_id=user_id,
                    permission_id=permission_id,
                    is_granted=is_granted,
                    is_active=True
                )
                db.add(user_permission)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
    
    def get_all_permissions(self, db: Session) -> List[models.Permission]:
        """Get all available permissions"""
        return db.query(models.Permission).all()
    
    def get_role_summary(self, db: Session) -> List[Dict]:
        """Get summary of all roles with their permissions and user counts"""
        summaries = []
        
        for role in UserRole:
            # Count users with this role
            user_count = db.query(models.User).filter(models.User.role == role).count()
            
            # Count permissions for this role
            permission_count = db.query(models.RolePermission).filter(
                and_(
                    models.RolePermission.role == role,
                    models.RolePermission.is_active == True
                )
            ).count()
            
            summaries.append({
                "role": role,
                "total_users": user_count,
                "total_permissions": permission_count,
                "is_active": True
            })
        
        return summaries

# Global RBAC service instance
rbac_service = RBACService() 