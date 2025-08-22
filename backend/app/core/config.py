from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Production-ready application settings"""
    
    # Basic settings
    PROJECT_NAME: str = "FinVoice AI Engine"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - Neon PostgreSQL with pgvector
    DATABASE_URL: str = "postgresql://user:password@localhost/finvoice"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/finvoice"
    DATABASE_ECHO: bool = False
    
    # Redis - Upstash for production
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_MARKET_DATA: int = 300  # 5 minutes
    REDIS_TTL_SESSION: int = 3600  # 1 hour
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Vapi AI Configuration
    VAPI_PRIVATE_KEY: Optional[str] = None  # Backend only
    VAPI_PUBLIC_KEY: Optional[str] = None   # Frontend safe
    VAPI_ASSISTANT_ID: Optional[str] = None
    VAPI_PHONE_NUMBER: Optional[str] = None
    VAPI_WEBHOOK_SECRET: Optional[str] = None
    VAPI_BASE_URL: str = "https://api.vapi.ai"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Market Data APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    EXCHANGE_RATE_API_KEY: Optional[str] = None
    
    # Google Cloud (TTS/STT fallback)
    GOOGLE_CLOUD_CREDENTIALS_PATH: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Blockchain - Production ready
    BLOCKCHAIN_PRIVATE_KEY: Optional[str] = None  # Never in code
    POLYGON_RPC_URL: str = "https://rpc-amoy.polygon.technology/"
    POLYGON_CHAIN_ID: int = 80002
    POLYGON_CURRENCY: str = "POL"
    POLYGON_EXPLORER: str = "https://amoy.polygonscan.com"
    WALLET_ADDRESS: Optional[str] = None
    CONTRACT_ADDRESS: Optional[str] = None
    
    # Banking APIs
    PLAID_CLIENT_ID: Optional[str] = None
    PLAID_SECRET: Optional[str] = None
    PLAID_ENV: str = "sandbox"
    
    # ML Models
    MODEL_PATH: str = str(Path(__file__).parent.parent.parent / "ml_models")
    
    # Logging and Monitoring
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: Optional[str] = None
    
    # Feature Flags
    DEMO_MODE: bool = False
    USE_MOCK_DATA: bool = False
    ENABLE_BLOCKCHAIN_LOGGING: bool = True
    ENABLE_VOICE_FEATURES: bool = True
    ENABLE_BANKING_APIS: bool = False
    
    # Performance
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
