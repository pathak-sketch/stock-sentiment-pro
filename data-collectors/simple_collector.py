Write-Host "🚀 Creating Full Twitter Collector..." -ForegroundColor Cyan

# Create the full simple_collector.py
@'
# data-collectors/simple_collector.py
import tweepy
import json
import logging
from datetime import datetime
import os
import sys
import time
import random

# Add the parent directory to Python path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.settings import settings
    print("✅ Loaded settings from config module")
except ImportError:
    print("⚠️ Could not import config.settings, using environment variables")
    # Fallback if config module isn't set up yet
    class Settings:
        TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
        TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
        TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
        TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")
    
    settings = Settings()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleTwitterCollector:
    def __init__(self):
        print("=" * 60)
        print("🧠 INITIALIZING TWITTER COLLECTOR")
        print("=" * 60)
        
        # Check if we have Twitter API keys
        has_keys = all([settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET, 
                       settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_SECRET])
        
        if not has_keys or "your_key_here" in settings.TWITTER_API_KEY:
            print("⚠️  TWITTER API KEYS NOT FOUND OR USING DEFAULT VALUES")
            print("   Using MOCK DATA for demonstration")
            print("   To use real Twitter data:")
            print("   1. Get API keys from developer.twitter.com")
            print("   2. Update your .env file")
            print("   3. Restart the script")
            print("-" * 60)
            self.use_mock_data = True
            self.client = None
        else:
            self.use_mock_data = False
            # Twitter API v2 Client
            try:
                print("🔑 Attempting to connect to Twitter API...")
                self.client = tweepy.Client(
                    bearer_token=settings.TWITTER_API_KEY,
                    consumer_key=settings.TWITTER_API_KEY,
                    consumer_secret=settings.TWITTER_API_SECRET,
                    access_token=settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=settings.TWITTER_ACCESS_SECRET,
                    wait_on_rate_limit=True
                )
                print("✅ Twitter API connected successfully!")
                print(f"   Using API Key: {settings.TWITTER_API_KEY[:10]}...")
            except Exception as e:
                print(f"❌ Failed to connect to Twitter: {e}")
                print("   Falling back to mock data")
                self.use_mock_data = True
        
        # Stocks to track
        self.stocks = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA']
        print(f"📊 Tracking stocks: {', '.join([f'${s}' for s in self.stocks])}")
        print("=" * 60)
    
    def search_recent_tweets(self, query: str, max_results: int = 10):
        """Search for recent tweets"""
        print(f"\n🔍 SEARCHING: {query}")
        
        # If using mock data (no API keys or API failed)
        if self.use_mock_data:
            print("   Using MOCK DATA (no valid Twitter API keys)")
            return self.get_mock_tweets(query, max_results)
        
        try:
            print("   Connecting to Twitter API...")
            response = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id']
            )
            
            tweets = []
            if response.data:
                for tweet in response.data:
                    tweet_data = {
                        'id': str(tweet.id),
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat() if tweet.created_at else datetime.utcnow().isoformat(),
                        'author_id': str(tweet.author_id),
                        'source': 'twitter',
                        'timestamp': datetime.utcnow().isoformat(),
                        'symbols': self.extract_symbols(tweet.text),
                        'public_metrics': {
                            'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                            'reply_count': tweet.public_metrics.get('reply_count', 0),
                            'like_count': tweet.public_metrics.get('like_count', 0),
                            'quote_count': tweet.public_metrics.get('quote_count', 0)
                        }
                    }
                    tweets.append(tweet_data)
                
                print(f"   ✅ Found {len(tweets)} real tweets from Twitter!")
            else:
                print(f"   ⚠️  No tweets found for: {query}")
                tweets = self.get_mock_tweets(query, max_results)
            
            return tweets
            
        except Exception as e:
            print(f"   ❌ Twitter API error: {e}")
            print("   Falling back to mock data")
            return self.get_mock_tweets(query, max_results)
    
    def get_mock_tweets(self, query: str, max_results: int):
        """Generate mock tweets for testing when API is not available"""
        
        # Extract symbol from query
        symbols = self.extract_symbols(query)
        symbol = symbols[0] if symbols else "TSLA"
        
        # Sentiment options
        sentiments = [
            f"${symbol} stock is soaring! 🚀 Great earnings report.",
            f"${symbol} facing headwinds this quarter. Concerns about growth.",
            f"${symbol} announced new product line. Investors excited!",
            f"I'm selling my ${symbol} shares. Too volatile for me.",
            f"${symbol} CEO just gave an amazing interview. Bullish!",
            f"Market analysts downgrade ${symbol}. Time to be cautious.",
            f"${symbol} partnership announcement boosted confidence.",
            f"Regulatory concerns for ${symbol}. Stock down 2% today."
        ]
        
        mock_tweets = []
        for i in range(min(max_results, 8)):
            tweet_text = random.choice(sentiments)
            mock_tweets.append({
                'id': f'mock_{int(time.time())}_{i}',
                'text': tweet_text,
                'created_at': datetime.utcnow().isoformat(),
                'author_id': f'mock_user_{i}',
                'source': 'mock',
                'timestamp': datetime.utcnow().isoformat(),
                'symbols': [symbol],
                'public_metrics': {
                    'retweet_count': random.randint(0, 100),
                    'reply_count': random.randint(0, 50),
                    'like_count': random.randint(0, 500),
                    'quote_count': random.randint(0, 20)
                }
            })
        
        print(f"   Generated {len(mock_tweets)} mock tweets for ${symbol}")
        return mock_tweets
    
    def extract_symbols(self, text: str):
        """Extract stock symbols from text"""
        symbols = []
        text_upper = text.upper()
        for stock in self.stocks:
            if f"${stock}" in text_upper:
                symbols.append(stock)
        return symbols
    
    def collect_all_stocks(self):
        """Collect tweets for all tracked stocks"""
        print("\n" + "=" * 60)
        print("📈 COLLECTING TWEETS FOR ALL STOCKS")
        print("=" * 60)
        
        all_tweets = []
        total_tweets = 0
        
        for stock in self.stocks:
            print(f"\n📊 Processing ${stock}...")
            query = f"${stock} -is:retweet lang:en"
            tweets = self.search_recent_tweets(query, max_results=5)
            all_tweets.extend(tweets)
            total_tweets += len(tweets)
            
            # Show sample tweet
            if tweets:
                sample = tweets[0]['text'][:80] + "..." if len(tweets[0]['text']) > 80 else tweets[0]['text']
                print(f"   Sample: {sample}")
            
            # Don't hit rate limits too fast (if using real API)
            if not self.use_mock_data:
                time.sleep(1)  # Wait 1 second between requests
        
        print("\n" + "=" * 60)
        print("📊 COLLECTION SUMMARY")
        print("=" * 60)
        
        # Count by symbol
        symbol_counts = {}
        for tweet in all_tweets:
            for symbol in tweet['symbols']:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        print(f"Total tweets collected: {total_tweets}")
        print("\nBreakdown by stock:")
        for symbol in self.stocks:
            count = symbol_counts.get(symbol, 0)
            print(f"  ${symbol}: {count} tweets")
        
        print("\nData source:", "REAL TWITTER API" if not self.use_mock_data else "MOCK DATA (for testing)")
        print("=" * 60)
        
        return all_tweets

# Main function
def main():
    print("\n" + "⭐" * 60)
    print("⭐                STOCK SENTIMENT ANALYZER v1.0                ⭐")
    print("⭐" * 60)
    
    collector = SimpleTwitterCollector()
    
    # Collect data
    tweets = collector.collect_all_stocks()
    
    # Show a few tweets
    print("\n📋 SAMPLE TWEETS COLLECTED:")
    print("-" * 40)
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"\n{i}. [{tweet['source'].upper()}] ${tweet['symbols'][0] if tweet['symbols'] else 'N/A'}")
        print(f"   {tweet['text']}")
        print(f"   👍 {tweet['public_metrics']['like_count']} likes | 🔄 {tweet['public_metrics']['retweet_count']} retweets")
    
    print("\n" + "=" * 60)
    print("🎉 COLLECTION COMPLETE!")
    print("=" * 60)
    
    # Next steps
    if collector.use_mock_data:
        print("\n🔧 NEXT STEPS TO USE REAL TWITTER DATA:")
        print("1. Go to: https://developer.twitter.com")
        print("2. Create a developer account (free)")
        print("3. Create a Project and App")
        print("4. Get your API Keys:")
        print("   - API Key")
        print("   - API Secret")
        print("   - Access Token")
        print("   - Access Token Secret")
        print("5. Update your .env file with these keys")
        print("6. Run this script again!")
    else:
        print("\n✅ SUCCESS! Using real Twitter data.")
        print("Next: Add sentiment analysis and database storage!")
    
    print("\n" + "⭐" * 60)

# Run if executed directly
if __name__ == "__main__":
    main()
'@ | Out-File -FilePath "data-collectors/simple_collector.py" -Encoding UTF8 -Force

Write-Host "✅ Created FULL version of simple_collector.py" -ForegroundColor Green