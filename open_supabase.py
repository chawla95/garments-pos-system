#!/usr/bin/env python3
"""
Open Supabase setup pages in browser
"""

import webbrowser
import time

def open_supabase_setup():
    """Open Supabase setup pages"""
    print("🌐 Opening Supabase setup pages...")
    
    # Open Supabase main page
    print("📋 Opening Supabase.com...")
    webbrowser.open("https://supabase.com")
    
    time.sleep(2)
    
    # Open Supabase dashboard (if user is logged in)
    print("📊 Opening Supabase Dashboard...")
    webbrowser.open("https://supabase.com/dashboard")
    
    time.sleep(2)
    
    # Open new project page
    print("🆕 Opening New Project page...")
    webbrowser.open("https://supabase.com/dashboard/new")
    
    print("\n✅ Browser tabs opened!")
    print("\n📋 Next steps:")
    print("1. Sign up/login to Supabase")
    print("2. Create a new project named 'garments-pos-system'")
    print("3. Go to Settings → Database")
    print("4. Copy the 'URI' connection string")
    print("5. Run: python quick_supabase_setup.py \"your-connection-string\"")

if __name__ == "__main__":
    open_supabase_setup() 