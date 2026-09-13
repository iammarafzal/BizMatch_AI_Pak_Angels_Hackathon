from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BizMatch AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./bizmatch.db"
    
    # Dual-Key Failover Google Gemini API Keys
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_1: str = ""
    GEMINI_API_KEY_2: str = ""

    # JWT Authentication & Authorization
    SECRET_KEY: str = "super_secret_bizmatch_key_2026_jwt_token_auth"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    PORT: int = 8000

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

