import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLiteStockDB:
    """SQLite database for stock sentiment - Zero setup, works everywhere!"""
    
    def __init__(self, db_path: str = "stock_sentiment.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tweets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_id TEXT UNIQUE,
                    text TEXT,
                    created_at TIMESTAMP,
                    author_id TEXT,
                    author_name TEXT,
                    author_followers INTEGER,
                    symbol TEXT,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    confidence REAL,
                    like_count INTEGER,
                    retweet_count INTEGER,
                    reply_count INTEGER,
                    quote_count INTEGER,
                    source TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sentiment_history table for time-series data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sentiment_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    timestamp TIMESTAMP,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    tweet_volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for fast queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_symbol ON tweets(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tweets_created ON tweets(created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_symbol_time ON sentiment_history(symbol, timestamp DESC)")
            
            conn.commit()
            logger.info(f"✅ SQLite database initialized at {self.db_path}")
    
    def save_tweet(self, tweet_data: Dict[str, Any]) -> bool:
        """Save a tweet to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO tweets (
                        tweet_id, text, created_at, author_id, author_name,
                        author_followers, symbol, sentiment_score, 
                        sentiment_label, confidence, like_count, 
                        retweet_count, reply_count, quote_count, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tweet_data.get('id'),
                    tweet_data.get('text', '')[:500],
                    tweet_data.get('created_at', datetime.utcnow()),
                    tweet_data.get('author_id'),
                    tweet_data.get('author_name'),
                    tweet_data.get('author_followers', 0),
                    tweet_data.get('symbol', '').upper(),
                    tweet_data.get('sentiment_score'),
                    tweet_data.get('sentiment_label'),
                    tweet_data.get('confidence'),
                    tweet_data.get('like_count', 0),
                    tweet_data.get('retweet_count', 0),
                    tweet_data.get('reply_count', 0),
                    tweet_data.get('quote_count', 0),
                    tweet_data.get('source', 'twitter')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to save tweet: {e}")
            return False
    
    def get_recent_sentiment(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Get recent sentiment for a stock"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    created_at,
                    text,
                    sentiment_score,
                    sentiment_label,
                    confidence,
                    like_count,
                    retweet_count
                FROM tweets
                WHERE symbol = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (symbol.upper(), limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_sentiment_summary(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Get sentiment summary for a stock"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tweets,
                    AVG(sentiment_score) as avg_sentiment,
                    SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive_count,
                    SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative_count,
                    SUM(CASE WHEN sentiment_label = 'neutral' THEN 1 ELSE 0 END) as neutral_count,
                    AVG(confidence) as avg_confidence,
                    MAX(created_at) as latest_tweet
                FROM tweets
                WHERE symbol = ? 
                AND datetime(created_at) > datetime('now', '-' || ? || ' hours')
            """, (symbol.upper(), hours))
            
            result = dict(cursor.fetchone())
            
            # Calculate percentages
            total = result.get('total_tweets', 0)
            if total > 0:
                result['positive_pct'] = round(result['positive_count'] / total * 100, 2)
                result['negative_pct'] = round(result['negative_count'] / total * 100, 2)
                result['neutral_pct'] = round(result['neutral_count'] / total * 100, 2)
            
            return result
    
    def get_market_summary(self) -> List[Dict]:
        """Get sentiment for all tracked stocks"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    symbol,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(*) as tweet_volume,
                    MAX(created_at) as last_update
                FROM tweets
                WHERE datetime(created_at) > datetime('now', '-1 hour')
                GROUP BY symbol
                ORDER BY avg_sentiment DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def log_sentiment_history(self, symbol: str, sentiment_score: float, 
                            sentiment_label: str, tweet_volume: int):
        """Log sentiment for time-series analysis"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sentiment_history 
                (symbol, timestamp, sentiment_score, sentiment_label, tweet_volume)
                VALUES (?, ?, ?, ?, ?)
            """, (symbol.upper(), datetime.utcnow(), sentiment_score, 
                  sentiment_label, tweet_volume))
            conn.commit()

# Create singleton instance
db = SQLiteStockDB()
