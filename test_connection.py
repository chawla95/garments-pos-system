#!/usr/bin/env python3
"""
Test Supabase Connection String
Usage: python test_connection.py "your-connection-string"
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse

def test_connection(connection_string):
    """Test the database connection"""
    print("🔧 Testing Supabase connection...")
    print(f"Connection string: {connection_string[:50]}...")
    
    try:
        # Parse the connection string
        parsed = urlparse(connection_string)
        print(f"✅ Connection string format is valid")
        print(f"   Host: {parsed.hostname}")
        print(f"   Port: {parsed.port}")
        print(f"   Database: {parsed.path[1:]}")
        print(f"   Username: {parsed.username}")
        
        # Test connection
        print("\n🔌 Attempting to connect...")
        conn = psycopg2.connect(connection_string)
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Connection successful!")
        print(f"   PostgreSQL version: {version[0]}")
        
        # Test if we can create a table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insert test data
        cursor.execute("""
            INSERT INTO test_connection (message) 
            VALUES ('Connection test successful') 
            ON CONFLICT DO NOTHING;
        """)
        
        # Query test data
        cursor.execute("SELECT COUNT(*) FROM test_connection;")
        count = cursor.fetchone()
        
        print(f"✅ Database operations successful!")
        print(f"   Test records: {count[0]}")
        
        # Clean up
        cursor.execute("DROP TABLE IF EXISTS test_connection;")
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Connection test PASSED!")
        print("Your Supabase connection is working correctly.")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if the password is correct")
        print("2. Verify the hostname and port")
        print("3. Make sure the Supabase project is active")
        print("4. Check if your IP is allowed (if using IP restrictions)")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python test_connection.py \"your-connection-string\"")
        print("\nExample:")
        print("python test_connection.py \"postgresql://postgres.xxx:password@aws-0-ap-south-1.pooler.supabase.com:6543/postgres\"")
        return
    
    connection_string = sys.argv[1]
    test_connection(connection_string)

if __name__ == "__main__":
    main() 