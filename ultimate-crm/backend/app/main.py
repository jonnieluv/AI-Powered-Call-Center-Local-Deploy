"""
Ultimate CRM System - Main Application
VAST Architecture Implementation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import time

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.exceptions import CRMException


# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Ultimate CRM System")
    
    # Initialize database
    await init_db()
    
    # Initialize AI agents (will be implemented in agents layer)
    # await initialize_agents()
    
    logger.info("Application startup complete")
    yield
    
    logger.info("Shutting down Ultimate CRM System")


# Create FastAPI application
app = FastAPI(
    title="Ultimate CRM System",
    description="Comprehensive CRM system built on VAST architecture with AI-driven automation",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=f"{process_time:.4f}s"
    )
    
    return response


@app.exception_handler(CRMException)
async def crm_exception_handler(request: Request, exc: CRMException):
    """Handle custom CRM exceptions"""
    logger.error(
        "CRM Exception",
        error=str(exc),
        status_code=exc.status_code,
        url=str(request.url)
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_type,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        url=str(request.url),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )


# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ultimate CRM System API",
        "version": "1.0.0",
        "architecture": "VAST (Vertical AI System Topology)",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "api": "operational",
            "database": "operational",  # Will be dynamic
            "cache": "operational",     # Will be dynamic
            "ai_agents": "operational"  # Will be dynamic
        }
    }