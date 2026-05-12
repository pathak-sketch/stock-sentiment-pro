# data-collectors/simple_collector.py
import tweepy
import json
import logging
from datetime import datetime
import os
import sys

# Add the parent directory to Python path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config.settings import settings
except ImportError:
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
        # Check if we have Twitter API keys
        if not all([settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET, 
                    settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_SECRET]):
            logger.warning("⚠️ Twitter API keys not found. Using mock data for testing.")
            self.use_mock_data = True
            self.client = None
        else:
            self.use_mock_data = False
            # Twitter API v2 Client
            try:
                self.client = tweepy.Client(
                    bearer_token=settings.TWITTER_API_KEY,
                    consumer_key=settings.TWITTER_API_KEY,
                    consumer_secret=settings.TWITTER_API_SECRET,
                    access_token=settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=settings.TWITTER_ACCESS_SECRET,
                    wait_on_rate_limit=True
                )
                logger.info("✅ Twitter client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twitter client: {e}")
                self.use_mock_data = True
        
        # Stocks to track
        self.stocks = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA']
    
    def search_recent_tweets(self, query: str, max_results: int = 10):
        """Search for recent tweets"""
        # If using mock data (no API keys or API failed)
        if self.use_mock_data:
            logger.info("📋 Using mock data (no Twitter API keys)")
            return self.get_mock_tweets(query, max_results)
        
        try:
            logger.info(f"🔍 Searching Twitter for: {query}")
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
                
                logger.info(f"✅ Found {len(tweets)} tweets for query: {query}")
            else:
                logger.info(f"⚠️ No tweets found for query: {query}")
            
            return tweets
            
        except Exception as e:
            logger.error(f"❌ Error searching tweets: {e}")
            # Fall back to mock data
            return self.get_mock_tweets(query, max_results)
    
    def get_mock_tweets(self, query: str, max_results: int):
        """Generate mock tweets for testing when API is not available"""
        import time
        import random
        
        # Extract symbol from query
        symbols = self.extract_symbols(query)
        symbol = symbols[0] if symbols else "TSLA"
        
        mock_tweets = [
            {
                'id': f'mock_{int(time.time())}_{i}',
                'text': f'${symbol} stock is {'up' if random.random() > 0.5 else 'down'} today! Great earnings report.',
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
            }
            for i in range(min(max_results, 5))
        ]
        
        # Add some negative/neutral tweets for variety
        if len(mock_tweets) > 1:
            mock_tweets[1]['text'] = f'I\'m concerned about ${symbol} future prospects. The competition is tough.'
        if len(mock_tweets) > 2:
            mock_tweets[2]['text'] = f'${symbol} announced quarterly results meeting expectations.'
        
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
        all_tweets = []
        
        for stock in self.stocks:
            logger.info(f"📊 Collecting tweets for ${stock}")
            query = f"${stock} -is:retweet lang:en"
            tweets = self.search_recent_tweets(query, max_results=5)
            all_tweets.extend(tweets)
            
            # Don't hit rate limits too fast
            if not self.use_mock_data:
                import time
                time.sleep(2)  # Wait 2 seconds between requests
        
        return all_tweets

# Test function
def test_collector():
    """Test the collector"""
    print("🧪 Testing Twitter Collector...")
    print("="*50)
    
    collector = SimpleTwitterCollector()
    
    # Test single stock
    print("\n1. Testing single stock search...")
    tweets = collector.search_recent_tweets("$TSLA -is:retweet lang:en", max_results=3)
    
    print(f"   Found {len(tweets)} tweets")
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"   {i}. {tweet['text'][:80]}...")
        print(f"      Symbols: {tweet['symbols']}")
        print(f"      Source: {tweet['source']}")
    
    # Test all stocks
    print("\n2. Testing all stocks collection...")
    all_tweets = collector.collect_all_stocks()
    print(f"   Total tweets collected: {len(all_tweets)}")
    
    # Count by symbol
    symbol_counts = {}
    for tweet in all_tweets:
        for symbol in tweet['symbols']:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    
    print("   Breakdown by symbol:")
    for symbol, count in symbol_counts.items():
        print(f"      ${symbol}: {count} tweets")
    
    print("\n" + "="*50)
    if collector.use_mock_data:
        print("⚠️  Using MOCK DATA (no Twitter API keys detected)")
        print("   To use real Twitter data:")
        print("   1. Get API keys from developer.twitter.com")
        print("   2. Add them to .env file")
        print("   3. Restart the script")
    else:
        print("✅ Twitter API is working!")
    
    return all_tweets

# Run the test if this file is executed directly
if __name__ == "__main__":
    test_collector()