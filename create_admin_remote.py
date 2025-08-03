#!/usr/bin/env python3
"""
Script to create admin user on remote backend
"""

import requests
import json

def create_admin_remote():
    """Create admin user on remote backend"""
    url = "https://garments-pos-backend.onrender.com/auth/register"
    
    payload = {
        "username": "admin_remote",
        "email": "admin_remote@pos.com", 
        "password": "admin123",
        "role": "admin"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Admin user created successfully!")
            print("Username: admin_remote")
            print("Password: admin123")
        else:
            print("❌ Failed to create admin user")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_admin_remote() 