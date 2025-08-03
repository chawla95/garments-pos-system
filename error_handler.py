import logging
import traceback
from typing import Union, Dict, Any
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
import psycopg
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomHTTPException(HTTPException):
    """Custom HTTP exception with detailed error information"""
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

class DatabaseConnectionError(CustomHTTPException):
    """Database connection error"""
    def __init__(self, detail: str = "Database connection failed"):
        super().__init__(status_code=503, detail=detail, error_code="DB_CONNECTION_ERROR")

class ValidationError(CustomHTTPException):
    """Data validation error"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=400, detail=detail, error_code="VALIDATION_ERROR")

class DependencyError(CustomHTTPException):
    """Dependency or import error"""
    def __init__(self, detail: str = "Dependency error"):
        super().__init__(status_code=500, detail=detail, error_code="DEPENDENCY_ERROR")

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all unhandled exceptions"""
    
    # Log the error with context
    logger.error(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Determine error type and response
    if isinstance(exc, CustomHTTPException):
        status_code = exc.status_code
        detail = exc.detail
        error_code = exc.error_code
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
        error_code = "HTTP_ERROR"
    elif isinstance(exc, RequestValidationError):
        status_code = 422
        detail = "Request validation error"
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, ValidationError):
        status_code = 400
        detail = "Data validation error"
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, SQLAlchemyError):
        status_code = 503
        detail = "Database error"
        error_code = "DATABASE_ERROR"
    elif isinstance(exc, (psycopg.Error, psycopg2.Error)):
        status_code = 503
        detail = "Database connection error"
        error_code = "DB_CONNECTION_ERROR"
    elif isinstance(exc, ImportError):
        status_code = 500
        detail = "Dependency error"
        error_code = "DEPENDENCY_ERROR"
    elif isinstance(exc, ModuleNotFoundError):
        status_code = 500
        detail = "Module not found"
        error_code = "MODULE_ERROR"
    else:
        status_code = 500
        detail = "Internal server error"
        error_code = "INTERNAL_ERROR"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": detail,
                "type": type(exc).__name__
            }
        }
    )

def setup_error_handlers(app):
    """Setup error handlers for the FastAPI app"""
    
    # Add global exception handler
    app.add_exception_handler(Exception, global_exception_handler)
    
    # Add specific exception handlers
    app.add_exception_handler(CustomHTTPException, global_exception_handler)
    app.add_exception_handler(HTTPException, global_exception_handler)
    app.add_exception_handler(RequestValidationError, global_exception_handler)
    app.add_exception_handler(ValidationError, global_exception_handler)
    app.add_exception_handler(SQLAlchemyError, global_exception_handler)
    app.add_exception_handler(ImportError, global_exception_handler)
    app.add_exception_handler(ModuleNotFoundError, global_exception_handler)

def validate_dependencies():
    """Validate all critical dependencies are available"""
    errors = []
    
    try:
        import fastapi
        logger.info(f"FastAPI version: {fastapi.__version__}")
    except ImportError as e:
        errors.append(f"FastAPI import error: {e}")
    
    try:
        import pydantic
        logger.info(f"Pydantic version: {pydantic.__version__}")
    except ImportError as e:
        errors.append(f"Pydantic import error: {e}")
    
    try:
        import sqlalchemy
        logger.info(f"SQLAlchemy version: {sqlalchemy.__version__}")
    except ImportError as e:
        errors.append(f"SQLAlchemy import error: {e}")
    
    try:
        import psycopg
        logger.info("psycopg3 available")
    except ImportError:
        try:
            import psycopg2
            logger.info("psycopg2 available")
        except ImportError as e:
            errors.append(f"PostgreSQL driver import error: {e}")
    
    if errors:
        raise DependencyError(f"Dependency validation failed: {'; '.join(errors)}")
    
    logger.info("All dependencies validated successfully")

def validate_database_connection():
    """Validate database connection"""
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection validated successfully")
    except Exception as e:
        logger.error(f"Database connection validation failed: {e}")
        raise DatabaseConnectionError(f"Database connection failed: {e}")

def health_check() -> Dict[str, Any]:
    """Comprehensive health check"""
    try:
        # Validate dependencies
        validate_dependencies()
        
        # Validate database connection
        validate_database_connection()
        
        return {
            "status": "healthy",
            "dependencies": "ok",
            "database": "ok"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "type": type(e).__name__
        } 