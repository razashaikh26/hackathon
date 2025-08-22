from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from typing import AsyncGenerator
import structlog
import redis.asyncio as redis
from app.core.config import settings

logger = structlog.get_logger()

# Shared Base for all models
Base = declarative_base()

# Metadata with pgvector support
metadata = Base.metadata
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Base class for models
Base = declarative_base(metadata=metadata)

# Redis connection
redis_client = None

async def init_redis():
    """Initialize Redis connection with better error handling"""
    global redis_client
    try:
        # Use Redis URL if available, otherwise skip Redis
        if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await redis_client.ping()
            logger.info("Redis connected successfully")
        else:
            logger.info("Redis URL not configured, skipping Redis initialization")
            redis_client = None
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Application will continue without caching.")
        redis_client = None

async def get_redis():
    """Get Redis client with fallback handling"""
    global redis_client
    if redis_client is None:
        logger.warning("Redis not available, operations will skip caching")
        return None
    try:
        # Test if connection is still alive
        await redis_client.ping()
        return redis_client
    except Exception as e:
        logger.warning(f"Redis connection lost: {e}")
        redis_client = None
        return None

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

def get_session():
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

async def init_db():
    """Initialize database with proper error handling"""
    try:
        # Import all models to ensure they are registered
        from app.db import models  # noqa
        
        async with async_engine.begin() as conn:
            # Enable pgvector extension (skip if not available)
            try:
                from sqlalchemy import text
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception as e:
                logger.warning(f"Could not create vector extension: {e}")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
        # Initialize Redis
        await init_redis()
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Don't raise to allow app to continue without database
        pass

async def close_db():
    """Cleanup database connections"""
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        
        if redis_client:
            await redis_client.close()
        
        logger.info("Database connections closed")
        
    except Exception as e:
        logger.error(f"Error closing database: {e}")

# Dependency functions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """Dependency for sync database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
