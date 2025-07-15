import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "PolyMaster"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Polymarket Configuration
    POLYGON_WALLET_PRIVATE_KEY: Optional[str] = None
    CLOB_API_KEY: Optional[str] = None
    CLOB_SECRET: Optional[str] = None
    CLOB_PASS_PHRASE: Optional[str] = None
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # News Configuration
    NEWSAPI_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    
    # Trading Configuration
    DRY_RUN: bool = True
    MARKET_CATEGORY: Optional[str] = None
    MIN_MARKET_VOLUME: float = 10000.0
    
    # Database Configuration
    CHROMA_DB_PATH: str = "./chroma_db"
    
    # WebSocket Configuration
    WS_UPDATE_INTERVAL: int = 5  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()