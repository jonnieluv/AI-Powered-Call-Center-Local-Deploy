"""
Custom exceptions for Ultimate CRM System
"""

from typing import Optional, Dict, Any


class CRMException(Exception):
    """Base exception class for CRM system"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_type: str = "crm_error",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)


# Authentication Exceptions
class AuthenticationException(CRMException):
    """Authentication related exceptions"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, error_type="authentication_error", **kwargs)


class AuthorizationException(CRMException):
    """Authorization related exceptions"""
    
    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(message, status_code=403, error_type="authorization_error", **kwargs)


class TokenExpiredException(AuthenticationException):
    """Token expiration exception"""
    
    def __init__(self, message: str = "Token has expired", **kwargs):
        super().__init__(message, **kwargs)


# Data Exceptions
class DataNotFoundException(CRMException):
    """Data not found exception"""
    
    def __init__(self, resource: str, identifier: str = None, **kwargs):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message, status_code=404, error_type="not_found_error", **kwargs)


class DataValidationException(CRMException):
    """Data validation exception"""
    
    def __init__(self, message: str = "Data validation failed", validation_errors: Dict = None, **kwargs):
        details = {"validation_errors": validation_errors} if validation_errors else {}
        super().__init__(message, status_code=422, error_type="validation_error", details=details, **kwargs)


class DataIntegrityException(CRMException):
    """Data integrity exception"""
    
    def __init__(self, message: str = "Data integrity constraint violated", **kwargs):
        super().__init__(message, status_code=409, error_type="integrity_error", **kwargs)


class DuplicateDataException(DataIntegrityException):
    """Duplicate data exception"""
    
    def __init__(self, resource: str, field: str = None, **kwargs):
        message = f"Duplicate {resource}"
        if field:
            message += f" for field: {field}"
        super().__init__(message, **kwargs)


# Business Logic Exceptions
class BusinessLogicException(CRMException):
    """Business logic violation exception"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=400, error_type="business_logic_error", **kwargs)


class InsufficientPermissionsException(BusinessLogicException):
    """Insufficient permissions for operation"""
    
    def __init__(self, operation: str, **kwargs):
        message = f"Insufficient permissions for operation: {operation}"
        super().__init__(message, **kwargs)


class InvalidStateException(BusinessLogicException):
    """Invalid state for operation"""
    
    def __init__(self, current_state: str, required_state: str, **kwargs):
        message = f"Invalid state '{current_state}', required state: '{required_state}'"
        super().__init__(message, **kwargs)


# External Service Exceptions
class ExternalServiceException(CRMException):
    """External service related exceptions"""
    
    def __init__(self, service: str, message: str = None, **kwargs):
        message = message or f"External service error: {service}"
        super().__init__(message, status_code=502, error_type="external_service_error", **kwargs)


class EmailServiceException(ExternalServiceException):
    """Email service exception"""
    
    def __init__(self, message: str = "Email service error", **kwargs):
        super().__init__("email", message, **kwargs)


class PaymentServiceException(ExternalServiceException):
    """Payment service exception"""
    
    def __init__(self, message: str = "Payment service error", **kwargs):
        super().__init__("payment", message, **kwargs)


# AI/ML Exceptions
class AIServiceException(CRMException):
    """AI service related exceptions"""
    
    def __init__(self, message: str = "AI service error", **kwargs):
        super().__init__(message, status_code=503, error_type="ai_service_error", **kwargs)


class ModelNotFoundException(AIServiceException):
    """ML model not found exception"""
    
    def __init__(self, model_name: str, **kwargs):
        message = f"ML model not found: {model_name}"
        super().__init__(message, **kwargs)


class PredictionException(AIServiceException):
    """Prediction generation exception"""
    
    def __init__(self, message: str = "Failed to generate prediction", **kwargs):
        super().__init__(message, **kwargs)


# System Exceptions
class SystemException(CRMException):
    """System-level exceptions"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=500, error_type="system_error", **kwargs)


class DatabaseException(SystemException):
    """Database operation exception"""
    
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, **kwargs)


class CacheException(SystemException):
    """Cache operation exception"""
    
    def __init__(self, message: str = "Cache operation failed", **kwargs):
        super().__init__(message, **kwargs)


class QueueException(SystemException):
    """Message queue exception"""
    
    def __init__(self, message: str = "Queue operation failed", **kwargs):
        super().__init__(message, **kwargs)


# Rate Limiting Exceptions
class RateLimitException(CRMException):
    """Rate limiting exception"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, status_code=429, error_type="rate_limit_error", details=details, **kwargs)


# Configuration Exceptions
class ConfigurationException(SystemException):
    """Configuration error exception"""
    
    def __init__(self, setting: str, message: str = None, **kwargs):
        message = message or f"Configuration error for setting: {setting}"
        super().__init__(message, **kwargs)