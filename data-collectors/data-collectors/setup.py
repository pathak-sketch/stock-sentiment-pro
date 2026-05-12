# setup.py
import os
import subprocess

def setup_project():
    print("🚀 Setting up Stock Sentiment Analyzer...")
    
    # Create necessary files if they don't exist
    files_to_create = {
        "config/settings.py": """from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    TWITTER_API_KEY: Optional[str] = os.getenv("TWITTER_API_KEY", "")
    TWITTER_API_SECRET: Optional[str] = os.getenv("TWITTER_API_SECRET", "")
    TWITTER_ACCESS_TOKEN: Optional[str] = os.getenv("TWITTER_ACCESS_TOKEN", "")
    TWITTER_ACCESS_SECRET: Optional[str] = os.getenv("TWITTER_ACCESS_SECRET", "")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "stock_sentiment"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    NEWSAPI_KEY: Optional[str] = os.getenv("NEWSAPI_KEY", "")

settings = Settings()""",
        
        "data-collectors/simple_collector.py": """import tweepy
import logging
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.settings import settings
except:
    class Settings:
        TWITTER_API_KEY = ""
        TWITTER_API_SECRET = ""
    
    settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTwitterCollector:
    def __init__(self):
        self.stocks = ['TSLA', 'AAPL', 'MSFT']
    
    def search_recent_tweets(self, query, max_results=3):
        print(f"🔍 Would search for: {query}")
        return [{'text': f'Mock tweet about {query}', 'symbols': ['TSLA']}]
    
    def collect_all_stocks(self):
        print("📊 Collecting mock data...")
        return [{'text': 'Mock data for testing', 'symbols': ['TSLA']}]

if __name__ == "__main__":
    collector = SimpleTwitterCollector()
    collector.collect_all_stocks()
    print("✅ Test completed!")"""
    }
    
    # Create files
    for filepath, content in files_to_create.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Created: {filepath}")
    
    print("\n📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "tweepy", "python-dotenv"])
    
    print("\n🎉 Setup complete!")
    print("Next steps:")
    print("1. Get Twitter API keys from developer.twitter.com")
    print("2. Create .env file with your keys")
    print("3. Run: python data-collectors/simple_collector.py")

if __name__ == "__main__":
    setup_project()