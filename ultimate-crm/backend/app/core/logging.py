"""
Structured logging configuration for Ultimate CRM System
"""

import logging
import sys
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add timestamp
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Add custom processors
            add_correlation_id,
            add_user_context,
            # Final processor based on format
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper())
    )
    
    # Silence noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def add_correlation_id(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log entries"""
    # This would typically come from request context
    # For now, we'll use a placeholder
    event_dict["correlation_id"] = getattr(logger, "_correlation_id", None)
    return event_dict


def add_user_context(logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add user context to log entries"""
    # This would typically come from request context
    # For now, we'll use a placeholder
    user_id = getattr(logger, "_user_id", None)
    if user_id:
        event_dict["user_id"] = user_id
    return event_dict


class CRMLogger:
    """Custom logger with CRM-specific functionality"""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def bind_correlation_id(self, correlation_id: str):
        """Bind correlation ID to logger"""
        return self.logger.bind(correlation_id=correlation_id)
    
    def bind_user_context(self, user_id: str, user_email: str = None):
        """Bind user context to logger"""
        context = {"user_id": user_id}
        if user_email:
            context["user_email"] = user_email
        return self.logger.bind(**context)
    
    def bind_customer_context(self, customer_id: str, customer_name: str = None):
        """Bind customer context to logger"""
        context = {"customer_id": customer_id}
        if customer_name:
            context["customer_name"] = customer_name
        return self.logger.bind(**context)
    
    def log_api_request(self, method: str, path: str, status_code: int, duration: float):
        """Log API request"""
        self.logger.info(
            "API request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2)
        )
    
    def log_database_query(self, query: str, params: Dict = None, duration: float = None):
        """Log database query"""
        log_data = {
            "event": "database_query",
            "query": query[:200] + "..." if len(query) > 200 else query
        }
        if params:
            log_data["params"] = params
        if duration:
            log_data["duration_ms"] = round(duration * 1000, 2)
        
        self.logger.debug("Database query", **log_data)
    
    def log_ai_prediction(self, model_name: str, input_features: Dict, prediction: Any, confidence: float = None):
        """Log AI prediction"""
        log_data = {
            "event": "ai_prediction",
            "model_name": model_name,
            "prediction": prediction
        }
        if confidence:
            log_data["confidence"] = confidence
        
        self.logger.info("AI prediction generated", **log_data)
    
    def log_business_event(self, event_type: str, entity_type: str, entity_id: str, details: Dict = None):
        """Log business event"""
        log_data = {
            "event": "business_event",
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id
        }
        if details:
            log_data.update(details)
        
        self.logger.info("Business event", **log_data)
    
    def log_security_event(self, event_type: str, user_id: str = None, ip_address: str = None, details: Dict = None):
        """Log security event"""
        log_data = {
            "event": "security_event",
            "event_type": event_type
        }
        if user_id:
            log_data["user_id"] = user_id
        if ip_address:
            log_data["ip_address"] = ip_address
        if details:
            log_data.update(details)
        
        self.logger.warning("Security event", **log_data)
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = None, tags: Dict = None):
        """Log performance metric"""
        log_data = {
            "event": "performance_metric",
            "metric_name": metric_name,
            "value": value
        }
        if unit:
            log_data["unit"] = unit
        if tags:
            log_data["tags"] = tags
        
        self.logger.info("Performance metric", **log_data)
    
    def log_integration_event(self, service_name: str, event_type: str, success: bool, details: Dict = None):
        """Log integration event"""
        log_data = {
            "event": "integration_event",
            "service_name": service_name,
            "event_type": event_type,
            "success": success
        }
        if details:
            log_data.update(details)
        
        level = "info" if success else "error"
        getattr(self.logger, level)("Integration event", **log_data)


def get_logger(name: str) -> CRMLogger:
    """Get a CRM logger instance"""
    return CRMLogger(name)