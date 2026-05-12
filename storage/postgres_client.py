# storage/postgres_client.py
import asyncpg
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresClient:
    """Production PostgreSQL client with connection pooling"""
    
    def __init__(self):
        self.pool = None
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'stock_sentiment'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password123'),
            'min_size': 10,
            'max_size': 50,
            'max_queries': 50000,
            'max_inactive_connection_lifetime': 300,
            'command_timeout': 60
        }
    
    async def connect(self):
        """Create production connection pool"""
        try:
            self.pool = await asyncpg.create_pool(**self.db_config)
            logger.info("✅ PostgreSQL connection pool created")
            
            # Initialize tables
            await self.init_tables()
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    async def init_tables(self):
        """Initialize database schema with TimescaleDB extensions"""
        async with self.pool.acquire() as conn:
            # Enable TimescaleDB extension
            await conn.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;')
            
            # Create tweets table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS tweets (
                    id BIGSERIAL PRIMARY KEY,
                    tweet_id VARCHAR(50) UNIQUE,
                    text TEXT,
                    created_at TIMESTAMPTZ NOT NULL,
                    author_id VARCHAR(50),
                    author_name VARCHAR(100),
                    author_followers INTEGER,
                    symbol VARCHAR(10),
                    sentiment_score DECIMAL(4,3),
                    sentiment_label VARCHAR(10),
                    confidence DECIMAL(4,3),
                    like_count INTEGER DEFAULT 0,
                    retweet_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    quote_count INTEGER DEFAULT 0,
                    source VARCHAR(20) DEFAULT 'twitter',
                    collected_at TIMESTAMPTZ DEFAULT NOW(),
                    metadata JSONB DEFAULT '{}'
                );
            ''')
            
            # Create hypertable for time-series
            await conn.execute('''
                SELECT create_hypertable('tweets', 'created_at', 
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                );
            ''')
            
            # Create indexes
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_tweets_symbol ON tweets (symbol, created_at DESC);')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_tweets_sentiment ON tweets (sentiment_score);')
            
            logger.info("✅ Database schema initialized")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        async with self.pool.acquire() as conn:
            yield conn
    
    async def save_tweet(self, tweet: Dict[str, Any]) -> bool:
        """Save tweet to database"""
        try:
            async with self.get_connection() as conn:
                await conn.execute('''
                    INSERT INTO tweets (
                        tweet_id, text, created_at, author_id, author_name,
                        author_followers, symbol, sentiment_score, 
                        sentiment_label, confidence, like_count, 
                        retweet_count, reply_count, quote_count, source, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    ON CONFLICT (tweet_id) DO NOTHING
                ''',
                    tweet.get('id'),
                    tweet.get('text', '')[:500],
                    tweet.get('created_at', datetime.utcnow()),
                    tweet.get('author_id'),
                    tweet.get('author_name'),
                    tweet.get('author_followers', 0),
                    tweet.get('symbol', '').upper(),
                    tweet.get('sentiment_score'),
                    tweet.get('sentiment_label'),
                    tweet.get('confidence'),
                    tweet.get('like_count', 0),
                    tweet.get('retweet_count', 0),
                    tweet.get('reply_count', 0),
                    tweet.get('quote_count', 0),
                    tweet.get('source', 'twitter'),
                    tweet.get('metadata', {})
                )
                return True
        except Exception as e:
            logger.error(f"❌ Failed to save tweet: {e}")
            return False
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        async with self.get_connection() as conn:
            # Overall market sentiment
            market = await conn.fetch('''
                SELECT 
                    symbol,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) as volume,
                    MAX(created_at) as last_update
                FROM tweets
                WHERE created_at > NOW() - INTERVAL '1 hour'
                GROUP BY symbol
                ORDER BY avg_sentiment DESC
            ''')
            
            # Sentiment distribution
            distribution = await conn.fetch('''
                SELECT 
                    sentiment_label,
                    COUNT(*) as count
                FROM tweets
                WHERE created_at > NOW() - INTERVAL '1 hour'
                GROUP BY sentiment_label
            ''')
            
            # Top trending stocks
            trending = await conn.fetch('''
                SELECT 
                    symbol,
                    COUNT(*) as tweet_volume,
                    AVG(sentiment_score) as sentiment
                FROM tweets
                WHERE created_at > NOW() - INTERVAL '30 minutes'
                GROUP BY symbol
                ORDER BY tweet_volume DESC
                LIMIT 5
            ''')
            
            # Recent activity
            recent = await conn.fetch('''
                SELECT 
                    symbol,
                    text,
                    sentiment_score,
                    sentiment_label,
                    created_at
                FROM tweets
                ORDER BY created_at DESC
                LIMIT 10
            ''')
            
            return {
                'market_sentiment': [dict(row) for row in market],
                'sentiment_distribution': [dict(row) for row in distribution],
                'trending_stocks': [dict(row) for row in trending],
                'recent_tweets': [dict(row) for row in recent],
                'timestamp': datetime.utcnow().isoformat()
            }

# Singleton instance
db = PostgresClient()