"""
Database configuration and connection management
Part of the DataBase - Universal Database Infrastructure
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
import asyncio
from typing import AsyncGenerator
import structlog

from app.core.config import settings, database_config
from app.core.exceptions import DatabaseException

logger = structlog.get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW,
    pool_timeout=database_config.POOL_TIMEOUT,
    pool_recycle=database_config.POOL_RECYCLE,
    echo=settings.DEBUG,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for migrations and initial setup
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW,
    pool_timeout=database_config.POOL_TIMEOUT,
    pool_recycle=database_config.POOL_RECYCLE,
    echo=settings.DEBUG,
)

# Create sync session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


# Database event listeners
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set database-specific configurations"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(async_engine.sync_engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log database queries in debug mode"""
    if settings.DEBUG:
        logger.debug(
            "Executing SQL",
            statement=statement[:200] + "..." if len(statement) > 200 else statement,
            parameters=parameters if len(str(parameters)) < 500 else "Large parameters"
        )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise DatabaseException(f"Database session error: {str(e)}")
        finally:
            await session.close()


def get_sync_session():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error("Database session error", error=str(e))
        raise DatabaseException(f"Database session error: {str(e)}")
    finally:
        db.close()


async def init_db():
    """Initialize database tables"""
    try:
        logger.info("Initializing database...")
        
        # Import all models to ensure they are registered
        from app.models import (
            user, customer, lead, opportunity, contact,
            activity, campaign, ticket, product, invoice
        )
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise DatabaseException(f"Database initialization failed: {str(e)}")


async def check_db_connection():
    """Check database connection health"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False


class DatabaseManager:
    """Database manager for advanced operations"""
    
    def __init__(self):
        self.async_engine = async_engine
        self.sync_engine = sync_engine
    
    async def execute_raw_query(self, query: str, params: dict = None):
        """Execute raw SQL query"""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(query, params or {})
                await session.commit()
                return result
        except Exception as e:
            logger.error("Raw query execution failed", query=query, error=str(e))
            raise DatabaseException(f"Raw query execution failed: {str(e)}")
    
    async def get_table_stats(self, table_name: str):
        """Get table statistics"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            async with AsyncSessionLocal() as session:
                result = await session.execute(query)
                return {"table": table_name, "count": result.scalar()}
        except Exception as e:
            logger.error("Failed to get table stats", table=table_name, error=str(e))
            raise DatabaseException(f"Failed to get table stats: {str(e)}")
    
    async def backup_table(self, table_name: str, backup_name: str):
        """Create table backup"""
        try:
            query = f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"
            await self.execute_raw_query(query)
            logger.info("Table backup created", table=table_name, backup=backup_name)
        except Exception as e:
            logger.error("Table backup failed", table=table_name, error=str(e))
            raise DatabaseException(f"Table backup failed: {str(e)}")
    
    async def optimize_database(self):
        """Perform database optimization"""
        try:
            # This would contain database-specific optimization queries
            # For PostgreSQL: VACUUM, ANALYZE, REINDEX
            queries = [
                "VACUUM ANALYZE",
                "REINDEX DATABASE ultimate_crm"
            ]
            
            for query in queries:
                await self.execute_raw_query(query)
            
            logger.info("Database optimization completed")
        except Exception as e:
            logger.error("Database optimization failed", error=str(e))
            raise DatabaseException(f"Database optimization failed: {str(e)}")


# Create global database manager instance
db_manager = DatabaseManager()