import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import settings

class WhatsAppService:
    def __init__(self):
        # Interakt API configuration from settings
        self.api_key = settings.INTERAKT_API_KEY
        self.api_secret = settings.INTERAKT_API_SECRET
        self.phone_number_id = settings.INTERAKT_PHONE_NUMBER_ID
        self.business_account_id = settings.INTERAKT_BUSINESS_ACCOUNT_ID
        
        self.base_url = "https://api.interakt.ai/v1"
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def send_text_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send a simple text message via WhatsApp"""
        try:
            # Format phone number (add country code if not present)
            if not phone_number.startswith('+91'):
                phone_number = f"+91{phone_number}"
            
            payload = {
                "phone_number": phone_number,
                "message": message,
                "channel": "whatsapp"
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Message sent successfully to {phone_number}")
                return {
                    "success": True,
                    "message_id": result.get("message_id"),
                    "status": "SENT"
                }
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "status": "FAILED"
                }
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "FAILED"
            }
    
    def send_template_message(self, phone_number: str, template_name: str, variables: Dict[str, str] = None) -> Dict[str, Any]:
        """Send a template message via WhatsApp"""
        try:
            # Format phone number
            if not phone_number.startswith('+91'):
                phone_number = f"+91{phone_number}"
            
            payload = {
                "phone_number": phone_number,
                "template_name": template_name,
                "channel": "whatsapp"
            }
            
            if variables:
                payload["variables"] = variables
            
            response = requests.post(
                f"{self.base_url}/messages/template",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Template message sent successfully to {phone_number}")
                return {
                    "success": True,
                    "message_id": result.get("message_id"),
                    "status": "SENT"
                }
            else:
                logger.error(f"Failed to send template message: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "status": "FAILED"
                }
                
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "FAILED"
            }
    
    def send_media_message(self, phone_number: str, media_url: str, caption: str = None) -> Dict[str, Any]:
        """Send a media message (image/document) via WhatsApp"""
        try:
            # Format phone number
            if not phone_number.startswith('+91'):
                phone_number = f"+91{phone_number}"
            
            payload = {
                "phone_number": phone_number,
                "media_url": media_url,
                "channel": "whatsapp"
            }
            
            if caption:
                payload["caption"] = caption
            
            response = requests.post(
                f"{self.base_url}/messages/media",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Media message sent successfully to {phone_number}")
                return {
                    "success": True,
                    "message_id": result.get("message_id"),
                    "status": "SENT"
                }
            else:
                logger.error(f"Failed to send media message: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "status": "FAILED"
                }
                
        except Exception as e:
            logger.error(f"Error sending media message: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "status": "FAILED"
            }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """Get the delivery status of a message"""
        try:
            response = requests.get(
                f"{self.base_url}/messages/{message_id}/status",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "status": result.get("status", "UNKNOWN"),
                    "delivered_at": result.get("delivered_at")
                }
            else:
                logger.error(f"Failed to get message status: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error getting message status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        # Remove any non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Check if it's a valid Indian phone number
        if cleaned.startswith('+91'):
            return len(cleaned) == 13  # +91 + 10 digits
        elif cleaned.startswith('91'):
            return len(cleaned) == 12  # 91 + 10 digits
        elif len(cleaned) == 10:
            return True  # 10 digits
        else:
            return False

# Global WhatsApp service instance
whatsapp_service = WhatsAppService() 