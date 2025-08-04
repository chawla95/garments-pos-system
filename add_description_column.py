#!/usr/bin/env python3
"""
Add description column to brands table
"""

import os
import sys
import logging
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_description_column():
    """Add description column to brands table"""
    try:
        from database import engine, SessionLocal
        
        logger.info("🔧 Adding description column to brands table...")
        
        # Check if column already exists
        db = SessionLocal()
        try:
            # Check if description column exists
            result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'brands' AND column_name = 'description'
            """))
            
            if result.fetchone():
                logger.info("✅ Description column already exists")
                return True
                
            # Add the column
            db.execute(text("ALTER TABLE brands ADD COLUMN description VARCHAR"))
            db.commit()
            logger.info("✅ Description column added successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding description column: {e}")
            db.rollback()
            return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting database migration...")
    
    if add_description_column():
        logger.info("🎉 Database migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Database migration failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 