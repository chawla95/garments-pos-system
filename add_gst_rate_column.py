#!/usr/bin/env python3
"""
Add gst_rate column to products table
"""

import os
import sys
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_gst_rate_column():
    """Add gst_rate column to products table"""
    try:
        from database import engine, SessionLocal
        
        logger.info("🔧 Adding gst_rate column to products table...")
        
        # Check if column already exists
        db = SessionLocal()
        try:
            # Check if gst_rate column exists
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products' AND column_name = 'gst_rate'
            """))
            
            if result.fetchone():
                logger.info("✅ gst_rate column already exists")
                return True
            else:
                # Add the column
                db.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN gst_rate FLOAT DEFAULT 12.0
                """))
                db.commit()
                logger.info("✅ gst_rate column added successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error adding gst_rate column: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database connection error: {e}")
        return False

if __name__ == "__main__":
    success = add_gst_rate_column()
    if success:
        print("✅ Database migration completed successfully")
    else:
        print("❌ Database migration failed")
        sys.exit(1) 