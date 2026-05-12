# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Twitter API Keys
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_SECRET", "")
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "stock_sentiment"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    
    # News API (optional)
    NEWSAPI_KEY: Optional[str] = os.getenv("NEWSAPI_KEY", "")
    
    class Config:
        env_file = ".env"

# Create settings instance
settings = Settings()

# Print debug info
if __name__ == "__main__":
    print("🔧 Settings Debug Info:")
    print(f"   ENV: {settings.ENV}")
    print(f"   Twitter API Key exists: {bool(settings.TWITTER_API_KEY)}")
    print(f"   Twitter API Secret exists: {bool(settings.TWITTER_API_SECRET)}")
    print(f"   .env file loaded: {os.path.exists('.env')}")