"""
Configuration settings for the POS system
"""

import os
from typing import Optional

class Settings:
    # Database settings
    DATABASE_URL: str = "sqlite:///./pos_system.db"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # WhatsApp Business API settings (Interakt)
    INTERAKT_API_KEY: Optional[str] = os.getenv("INTERAKT_API_KEY", "")
    INTERAKT_API_SECRET: Optional[str] = os.getenv("INTERAKT_API_SECRET", "")
    INTERAKT_PHONE_NUMBER_ID: Optional[str] = os.getenv("INTERAKT_PHONE_NUMBER_ID", "")
    INTERAKT_BUSINESS_ACCOUNT_ID: Optional[str] = os.getenv("INTERAKT_BUSINESS_ACCOUNT_ID", "")
    
    # WhatsApp configuration
    WHATSAPP_ENABLED: bool = bool(INTERAKT_API_KEY and INTERAKT_API_SECRET)
    
    # Shop details for invoices
    SHOP_NAME: str = "Your Garments Store"
    SHOP_ADDRESS: str = "123 Main Street, City, State 12345"
    SHOP_PHONE: str = "+91-9876543210"
    SHOP_EMAIL: str = "info@yourstore.com"
    SHOP_GSTIN: str = "22AAAAA0000A1Z5"  # Replace with your actual GSTIN
    
    # Default settings
    DEFAULT_GST_RATE: float = 12.0
    DEFAULT_CURRENCY: str = "INR"
    
    @classmethod
    def get_whatsapp_config(cls) -> dict:
        """Get WhatsApp configuration"""
        return {
            "api_key": cls.INTERAKT_API_KEY,
            "api_secret": cls.INTERAKT_API_SECRET,
            "phone_number_id": cls.INTERAKT_PHONE_NUMBER_ID,
            "business_account_id": cls.INTERAKT_BUSINESS_ACCOUNT_ID,
            "enabled": cls.WHATSAPP_ENABLED
        }
    
    @classmethod
    def is_whatsapp_configured(cls) -> bool:
        """Check if WhatsApp is properly configured"""
        return all([
            cls.INTERAKT_API_KEY,
            cls.INTERAKT_API_SECRET,
            cls.INTERAKT_PHONE_NUMBER_ID,
            cls.INTERAKT_BUSINESS_ACCOUNT_ID
        ])

# Global settings instance
settings = Settings() 