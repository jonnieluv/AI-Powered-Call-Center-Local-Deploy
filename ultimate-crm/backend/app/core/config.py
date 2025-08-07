"""
Core configuration settings for Ultimate CRM System
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql://crm_user:crm_password@localhost:5432/ultimate_crm",
        env="DATABASE_URL"
    )
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Neo4j
    NEO4J_URL: str = Field(default="bolt://localhost:7687", env="NEO4J_URL")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="crm_password", env="NEO4J_PASSWORD")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = Field(default="http://localhost:9200", env="ELASTICSEARCH_URL")
    
    # MinIO Object Storage
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="crm_admin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="crm_password", env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    
    # Email
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # ML/AI Settings
    ML_MODEL_PATH: str = Field(default="/models", env="ML_MODEL_PATH")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=8080, env="PROMETHEUS_PORT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Business Logic
    DEFAULT_TIMEZONE: str = Field(default="UTC", env="DEFAULT_TIMEZONE")
    DEFAULT_CURRENCY: str = Field(default="USD", env="DEFAULT_CURRENCY")
    
    # Feature Flags
    ENABLE_AI_AGENTS: bool = Field(default=True, env="ENABLE_AI_AGENTS")
    ENABLE_PREDICTIVE_ANALYTICS: bool = Field(default=True, env="ENABLE_PREDICTIVE_ANALYTICS")
    ENABLE_REAL_TIME_PROCESSING: bool = Field(default=True, env="ENABLE_REAL_TIME_PROCESSING")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


# Database configuration
class DatabaseConfig:
    """Database-specific configuration"""
    
    # Connection pool settings
    POOL_SIZE = 20
    MAX_OVERFLOW = 30
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600
    
    # Query settings
    QUERY_TIMEOUT = 30
    STATEMENT_TIMEOUT = 60
    
    # Migration settings
    ALEMBIC_CONFIG = "alembic.ini"


# Cache configuration
class CacheConfig:
    """Cache-specific configuration"""
    
    # Redis settings
    CONNECTION_POOL_SIZE = 50
    SOCKET_TIMEOUT = 5
    SOCKET_CONNECT_TIMEOUT = 5
    
    # Cache TTL settings (in seconds)
    DEFAULT_TTL = 3600  # 1 hour
    SHORT_TTL = 300     # 5 minutes
    LONG_TTL = 86400    # 24 hours
    
    # Cache keys
    USER_SESSION_PREFIX = "session:user:"
    CUSTOMER_CACHE_PREFIX = "cache:customer:"
    ANALYTICS_CACHE_PREFIX = "cache:analytics:"


# AI/ML configuration
class AIConfig:
    """AI/ML-specific configuration"""
    
    # Model settings
    DEFAULT_MODEL_BATCH_SIZE = 32
    MODEL_INFERENCE_TIMEOUT = 30
    
    # NLP settings
    SPACY_MODEL = "en_core_web_sm"
    SENTIMENT_THRESHOLD = 0.1
    
    # Prediction settings
    CHURN_PREDICTION_THRESHOLD = 0.7
    LEAD_SCORING_WEIGHTS = {
        "demographic": 0.3,
        "behavioral": 0.4,
        "engagement": 0.3
    }
    
    # Agent settings
    AGENT_UPDATE_INTERVAL = 300  # 5 minutes
    MAX_CONCURRENT_AGENTS = 10


# Export configurations
database_config = DatabaseConfig()
cache_config = CacheConfig()
ai_config = AIConfig()