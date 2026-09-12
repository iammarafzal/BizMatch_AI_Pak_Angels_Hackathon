import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ManageMatch AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # SQLite by default for hackathon setup
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./managematch.db")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()
