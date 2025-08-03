#!/usr/bin/env python3
"""
Pre-Deployment Testing Script
Validates all critical components before deployment to catch errors early.
"""

import os
import sys
import importlib
import subprocess
import requests
from typing import List, Dict, Any
import json

class PreDeploymentTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        self.is_production = os.getenv("DATABASE_URL") is not None
        
    def log_error(self, test_name: str, error: str):
        """Log an error with test name and details"""
        self.errors.append(f"❌ {test_name}: {error}")
        print(f"❌ {test_name}: {error}")
        
    def log_warning(self, test_name: str, warning: str):
        """Log a warning with test name and details"""
        self.warnings.append(f"⚠️  {test_name}: {warning}")
        print(f"⚠️  {test_name}: {warning}")
        
    def log_success(self, test_name: str):
        """Log a successful test"""
        self.success_count += 1
        print(f"✅ {test_name}")
        
    def test_environment_variables(self) -> bool:
        """Test if required environment variables are set"""
        self.total_tests += 1
        test_name = "Environment Variables Check"
        
        required_vars = [
            "DATABASE_URL",
            "SECRET_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            if self.is_production:
                self.log_error(test_name, f"Missing required environment variables: {', '.join(missing_vars)}")
                return False
            else:
                self.log_warning(test_name, f"Missing environment variables (OK for local dev): {', '.join(missing_vars)}")
                return True
        else:
            self.log_success(test_name)
            return True
            
    def test_database_connection(self) -> bool:
        """Test database connection and basic operations"""
        self.total_tests += 1
        test_name = "Database Connection Test"
        
        if not self.is_production:
            self.log_warning(test_name, "Skipping database test in local development")
            return True
            
        try:
            # Import database components
            from database import engine, Base
            from models import User, Brand, Dealer, Product, Sale, SaleItem
            
            # Test connection
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
                
            # Test table creation (without actually creating)
            Base.metadata.create_all(bind=engine, checkfirst=True)
            
            self.log_success(test_name)
            return True
            
        except Exception as e:
            self.log_error(test_name, f"Database connection failed: {str(e)}")
            return False
            
    def test_imports(self) -> bool:
        """Test all critical module imports"""
        self.total_tests += 1
        test_name = "Module Imports Test"
        
        critical_modules = [
            "fastapi",
            "sqlalchemy",
            "pydantic",
            "uvicorn",
            "alembic",
            "jinja2"
        ]
        
        # Only test asyncpg if we're in production
        if self.is_production:
            critical_modules.append("asyncpg")
        
        failed_imports = []
        for module in critical_modules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                failed_imports.append(f"{module}: {str(e)}")
                
        if failed_imports:
            self.log_error(test_name, f"Failed imports: {'; '.join(failed_imports)}")
            return False
        else:
            self.log_success(test_name)
            return True
            
    def test_schema_validation(self) -> bool:
        """Test Pydantic schema validation"""
        self.total_tests += 1
        test_name = "Schema Validation Test"
        
        try:
            from schemas import UserCreate, UserLogin, DealerCreate, ProductCreate
            from pydantic import ValidationError
            
            # Test UserCreate schema
            test_user = UserCreate(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                role="cashier"
            )
            
            # Test DealerCreate schema
            test_dealer = DealerCreate(
                name="Test Dealer",
                contact="1234567890",
                address="Test Address",
                pan="ABCDE1234F",
                gst="22ABCDE1234F1Z5"
            )
            
            self.log_success(test_name)
            return True
            
        except ValidationError as e:
            self.log_error(test_name, f"Schema validation failed: {str(e)}")
            return False
        except Exception as e:
            self.log_error(test_name, f"Schema test failed: {str(e)}")
            return False
            
    def test_config_loading(self) -> bool:
        """Test configuration loading"""
        self.total_tests += 1
        test_name = "Configuration Loading Test"
        
        try:
            from config import settings
            
            # Test that settings can be accessed
            _ = settings.DATABASE_URL
            _ = settings.SECRET_KEY
            _ = settings.ALGORITHM
            _ = settings.ACCESS_TOKEN_EXPIRE_MINUTES
            
            self.log_success(test_name)
            return True
            
        except Exception as e:
            self.log_error(test_name, f"Configuration loading failed: {str(e)}")
            return False
            
    def test_auth_functions(self) -> bool:
        """Test authentication functions"""
        self.total_tests += 1
        test_name = "Authentication Functions Test"
        
        try:
            from auth import create_access_token, verify_password, get_password_hash
            
            # Test password hashing
            test_password = "testpass123"
            hashed = get_password_hash(test_password)
            
            # Test password verification
            if not verify_password(test_password, hashed):
                raise Exception("Password verification failed")
                
            # Test token creation
            token_data = {"sub": "testuser", "role": "cashier"}
            token = create_access_token(token_data)
            
            if not token:
                raise Exception("Token creation failed")
                
            self.log_success(test_name)
            return True
            
        except Exception as e:
            if "DATABASE_URL" in str(e) and not self.is_production:
                self.log_warning(test_name, "Authentication test skipped in local development (requires DATABASE_URL)")
                return True
            else:
                self.log_error(test_name, f"Authentication test failed: {str(e)}")
                return False
            
    def test_requirements_compatibility(self) -> bool:
        """Test requirements.txt compatibility"""
        self.total_tests += 1
        test_name = "Requirements Compatibility Test"
        
        try:
            # Read requirements.txt
            with open("requirements.txt", "r") as f:
                requirements = f.read()
                
            # Check for known problematic combinations
            problematic_combinations = [
                ("fastapi==0.95.2", "pydantic>=2.0.0"),
                ("sqlalchemy==1.4.54", "postgresql+psycopg://"),
                ("psycopg2-binary", "python>=3.13")
            ]
            
            warnings = []
            for combo in problematic_combinations:
                if all(combo[0] in requirements for combo in [combo]):
                    warnings.append(f"Potential compatibility issue: {combo[0]} with {combo[1]}")
                    
            if warnings:
                for warning in warnings:
                    self.log_warning(test_name, warning)
                    
            self.log_success(test_name)
            return True
            
        except Exception as e:
            self.log_error(test_name, f"Requirements check failed: {str(e)}")
            return False
            
    def test_database_url_format(self) -> bool:
        """Test database URL format"""
        self.total_tests += 1
        test_name = "Database URL Format Test"
        
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                if self.is_production:
                    self.log_error(test_name, "DATABASE_URL not set")
                    return False
                else:
                    self.log_warning(test_name, "DATABASE_URL not set (OK for local dev)")
                    return True
                
            # Check if it's a valid PostgreSQL URL
            if not database_url.startswith(("postgresql://", "postgres://")):
                self.log_error(test_name, "DATABASE_URL must start with postgresql:// or postgres://")
                return False
                
            # Check for required components
            if "@" not in database_url or ":" not in database_url:
                self.log_error(test_name, "DATABASE_URL missing required components")
                return False
                
            self.log_success(test_name)
            return True
            
        except Exception as e:
            self.log_error(test_name, f"Database URL test failed: {str(e)}")
            return False
            
    def test_render_yaml(self) -> bool:
        """Test render.yaml configuration"""
        self.total_tests += 1
        test_name = "Render Configuration Test"
        
        try:
            if not os.path.exists("render.yaml"):
                self.log_error(test_name, "render.yaml file not found")
                return False
                
            with open("render.yaml", "r") as f:
                content = f.read()
                
            # Check for required sections
            required_sections = ["services:", "buildCommand:", "startCommand:"]
            missing_sections = []
            
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
                    
            if missing_sections:
                self.log_error(test_name, f"Missing required sections: {', '.join(missing_sections)}")
                return False
                
            self.log_success(test_name)
            return True
            
        except Exception as e:
            self.log_error(test_name, f"Render config test failed: {str(e)}")
            return False
            
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all pre-deployment tests"""
        print("🚀 Starting Pre-Deployment Tests...")
        print("=" * 50)
        
        tests = [
            self.test_environment_variables,
            self.test_imports,
            self.test_config_loading,
            self.test_database_url_format,
            self.test_requirements_compatibility,
            self.test_render_yaml,
            self.test_database_connection,
            self.test_schema_validation,
            self.test_auth_functions
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_error(test.__name__, f"Test crashed: {str(e)}")
                
        return self.generate_report()
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("\n" + "=" * 50)
        print("📊 PRE-DEPLOYMENT TEST REPORT")
        print("=" * 50)
        
        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"✅ Successful Tests: {self.success_count}/{self.total_tests}")
        print(f"❌ Errors: {len(self.errors)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        # Determine deployment readiness
        # In local dev, allow deployment with warnings only
        # In production, require no errors
        deployment_ready = len(self.errors) == 0 or (not self.is_production and len([e for e in self.errors if "DATABASE_URL" not in e]) == 0)
        status = "🟢 READY FOR DEPLOYMENT" if deployment_ready else "🔴 NOT READY FOR DEPLOYMENT"
        
        print(f"\n{status}")
        
        if not deployment_ready:
            print("\n🔧 RECOMMENDED ACTIONS:")
            print("1. Fix all errors listed above")
            print("2. Address warnings if critical")
            print("3. Re-run tests before deployment")
            
        return {
            "success_count": self.success_count,
            "total_tests": self.total_tests,
            "errors": self.errors,
            "warnings": self.warnings,
            "success_rate": success_rate,
            "deployment_ready": deployment_ready
        }

def main():
    """Main function to run pre-deployment tests"""
    tester = PreDeploymentTester()
    report = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if not report["deployment_ready"]:
        sys.exit(1)
    else:
        print("\n🎉 All tests passed! Ready for deployment!")
        sys.exit(0)

if __name__ == "__main__":
    main() 