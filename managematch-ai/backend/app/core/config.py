from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "BizMatch AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bizmatch"
    GEMINI_API_KEY: str = ""
    
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

settings = Settings()
