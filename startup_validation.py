#!/usr/bin/env python3
"""
Startup validation script for Garments POS System
Validates all critical dependencies and configurations before application startup
"""

import sys
import os
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StartupValidator:
    """Validates application startup requirements"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_checks = 0
        self.total_checks = 0
    
    def add_error(self, check_name: str, error: str):
        """Add an error to the validation results"""
        self.errors.append(f"{check_name}: {error}")
        self.total_checks += 1
    
    def add_warning(self, check_name: str, warning: str):
        """Add a warning to the validation results"""
        self.warnings.append(f"{check_name}: {warning}")
        self.total_checks += 1
    
    def add_success(self, check_name: str):
        """Add a successful check"""
        self.passed_checks += 1
        self.total_checks += 1
        logger.info(f"✅ {check_name}")
    
    def check_python_version(self):
        """Check Python version compatibility"""
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 8:
                self.add_success(f"Python version {version.major}.{version.minor}.{version.micro}")
            else:
                self.add_error("Python Version", f"Python 3.8+ required, got {version.major}.{version.minor}.{version.micro}")
        except Exception as e:
            self.add_error("Python Version", f"Could not determine Python version: {e}")
    
    def check_environment_variables(self):
        """Check required environment variables"""
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES"
        ]
        
        # Check if we're in production (has DATABASE_URL)
        is_production = os.getenv("DATABASE_URL") is not None
        
        for var in required_vars:
            if os.getenv(var):
                self.add_success(f"Environment variable {var}")
            else:
                if is_production:
                    self.add_error("Environment Variables", f"Missing required environment variable: {var}")
                else:
                    self.add_warning("Environment Variables", f"Missing environment variable {var} (OK for local dev)")
    
    def check_dependencies(self):
        """Check critical dependencies"""
        dependencies = [
            ("fastapi", "FastAPI"),
            ("pydantic", "Pydantic"),
            ("sqlalchemy", "SQLAlchemy"),
            ("uvicorn", "Uvicorn"),
            ("psycopg", "PostgreSQL Driver"),
            ("alembic", "Alembic"),
            ("jinja2", "Jinja2"),
            ("reportlab", "ReportLab"),
            ("requests", "Requests"),
            ("passlib", "PassLib"),
            ("jose", "Python-Jose"),
            ("multipart", "Python-Multipart"),
            ("dotenv", "Python-Dotenv")
        ]
        
        for module_name, display_name in dependencies:
            try:
                if module_name == "psycopg":
                    # Special handling for PostgreSQL driver
                    try:
                        import psycopg
                        self.add_success(f"{display_name} (psycopg3)")
                    except ImportError:
                        try:
                            import psycopg2
                            self.add_success(f"{display_name} (psycopg2)")
                        except ImportError:
                            self.add_error("Dependencies", f"PostgreSQL driver not found")
                else:
                    __import__(module_name.replace("-", "_"))
                    self.add_success(f"{display_name}")
            except ImportError as e:
                self.add_error("Dependencies", f"{display_name} not found: {e}")
    
    def check_database_connection(self):
        """Check database connection"""
        # Skip database check in local development
        if not os.getenv("DATABASE_URL"):
            self.add_warning("Database Connection", "Skipping database check in local development")
            return
            
        try:
            from database import engine
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            self.add_success("Database Connection")
        except Exception as e:
            self.add_error("Database Connection", f"Failed to connect to database: {e}")
    
    def check_sqlalchemy_models(self):
        """Check SQLAlchemy model imports"""
        try:
            from models import Base, User, Product, InventoryItem, Invoice
            self.add_success("SQLAlchemy Models")
        except Exception as e:
            self.add_error("SQLAlchemy Models", f"Failed to import models: {e}")
    
    def check_pydantic_schemas(self):
        """Check Pydantic schema imports"""
        try:
            from schemas import UserCreate, ProductCreate, InvoiceCreate
            self.add_success("Pydantic Schemas")
        except Exception as e:
            self.add_error("Pydantic Schemas", f"Failed to import schemas: {e}")
    
    def check_auth_module(self):
        """Check authentication module"""
        try:
            from auth import get_password_hash, verify_password, create_access_token
            self.add_success("Authentication Module")
        except Exception as e:
            # Skip auth check if it's due to missing DATABASE_URL in local dev
            if "DATABASE_URL" in str(e) and not os.getenv("DATABASE_URL"):
                self.add_warning("Authentication Module", "Skipping auth check in local development")
            else:
                self.add_error("Authentication Module", f"Failed to import auth module: {e}")
    
    def check_config_module(self):
        """Check configuration module"""
        try:
            from config import settings
            self.add_success("Configuration Module")
        except Exception as e:
            self.add_error("Configuration Module", f"Failed to import config module: {e}")
    
    def check_file_permissions(self):
        """Check file permissions for logs and uploads"""
        try:
            # Check if we can write to current directory
            test_file = "startup_test.tmp"
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            self.add_success("File Permissions")
        except Exception as e:
            self.add_error("File Permissions", f"Cannot write to filesystem: {e}")
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all validation checks"""
        logger.info("🚀 Starting application startup validation...")
        
        # Run all checks
        self.check_python_version()
        self.check_environment_variables()
        self.check_dependencies()
        self.check_database_connection()
        self.check_sqlalchemy_models()
        self.check_pydantic_schemas()
        self.check_auth_module()
        self.check_config_module()
        self.check_file_permissions()
        
        # Generate report
        success_rate = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        
        report = {
            "status": "healthy" if len(self.errors) == 0 else "unhealthy",
            "passed_checks": self.passed_checks,
            "total_checks": self.total_checks,
            "success_rate": f"{success_rate:.1f}%",
            "errors": self.errors,
            "warnings": self.warnings
        }
        
        # Log results
        logger.info(f"📊 Validation Results:")
        logger.info(f"   ✅ Passed: {self.passed_checks}/{self.total_checks}")
        logger.info(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if self.errors:
            logger.error(f"   ❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                logger.error(f"      - {error}")
        
        if self.warnings:
            logger.warning(f"   ⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                logger.warning(f"      - {warning}")
        
        if len(self.errors) == 0:
            logger.info("🎉 All startup checks passed! Application is ready to start.")
        else:
            logger.error("❌ Startup validation failed! Please fix the errors above.")
        
        return report

def main():
    """Main validation function"""
    validator = StartupValidator()
    report = validator.run_all_checks()
    
    # Exit with error code if validation failed
    if len(report["errors"]) > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 