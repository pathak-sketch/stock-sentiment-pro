# storage/db_client.py
import asyncpg
import logging
from datetime import datetime
from typing import List, Dict, Any
import json

from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseClient:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=5,
                max_size=20
            )
            logger.info("✅ Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def save_tweet(self, tweet: Dict[str, Any]) -> int:
        """Save tweet to database, return tweet_id"""
        async with self.pool.acquire() as conn:
            # Check if tweet already exists
            existing = await conn.fetchrow(
                "SELECT id FROM tweets WHERE tweet_id = $1",
                tweet['id']
            )
            
            if existing:
                return existing['id']
            
            # Insert new tweet
            tweet_id = await conn.fetchval("""
                INSERT INTO tweets 
                (tweet_id, text, created_at, author_id, source, symbols)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """,
                tweet['id'],
                tweet['text'],
                datetime.fromisoformat(tweet['created_at']),
                tweet['author_id'],
                tweet['source'],
                tweet['symbols']
            )
            
            return tweet_id
    
    async def save_sentiment(self, tweet_id: int, sentiment: Dict[str, Any]):
        """Save sentiment analysis results"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sentiment 
                (tweet_id, polarity, subjectivity, sentiment, confidence)
                VALUES ($1, $2, $3, $4, $5)
            """,
                tweet_id,
                sentiment.get('polarity', 0),
                sentiment.get('subjectivity', 0.5),
                sentiment.get('sentiment', 'neutral'),
                sentiment.get('confidence', 0)
            )
    
    async def get_daily_sentiment(self, symbol: str, days: int = 7) -> List[Dict]:
        """Get daily sentiment for a symbol"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    date_trunc('day', t.created_at) as date,
                    COUNT(*) as total_tweets,
                    AVG(s.polarity) as avg_polarity,
                    SUM(CASE WHEN s.sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
                    SUM(CASE WHEN s.sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count,
                    SUM(CASE WHEN s.sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_count
                FROM tweets t
                JOIN sentiment s ON t.id = s.tweet_id
                WHERE $1 = ANY(t.symbols)
                AND t.created_at >= CURRENT_DATE - INTERVAL '$2 days'
                GROUP BY date_trunc('day', t.created_at)
                ORDER BY date DESC
            """, symbol, days)
            
            return [dict(row) for row in rows]

# Test function
async def test_database():
    """Test database connection and operations"""
    db = DatabaseClient()
    await db.connect()
    
    # Test data
    test_tweet = {
        'id': '123456789',
        'text': 'Tesla stock is amazing! $TSLA',
        'created_at': datetime.utcnow().isoformat(),
        'author_id': '987654321',
        'source': 'twitter',
        'symbols': ['TSLA']
    }
    
    test_sentiment = {
        'polarity': 0.8,
        'subjectivity': 0.6,
        'sentiment': 'positive',
        'confidence': 0.9
    }
    
    # Save tweet
    tweet_id = await db.save_tweet(test_tweet)
    print(f"✅ Saved tweet with ID: {tweet_id}")
    
    # Save sentiment
    await db.save_sentiment(tweet_id, test_sentiment)
    print("✅ Saved sentiment analysis")
    
    # Query data
    sentiment_data = await db.get_daily_sentiment('TSLA', 7)
    print(f"📊 Daily sentiment data: {sentiment_data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_database())