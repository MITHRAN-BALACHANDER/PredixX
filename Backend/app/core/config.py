from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API
    PROJECT_NAME: str = "Dynamic Pricing Engine"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Database (SQLite for local development)
    DATABASE_URL: str = "sqlite+aiosqlite:///./dpe.db"
    DATABASE_URL_SYNC: str = "sqlite:///./dpe.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model
    MODEL_PATH: str = "./models/price_model.pkl"
    MODELS_DIR: str = "../amazon_price_model/artifacts"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
