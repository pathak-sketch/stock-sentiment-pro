-- ============================================
-- STOCK SENTIMENT DATABASE SCHEMA
-- ============================================

-- Drop tables if they exist (clean start)
DROP TABLE IF EXISTS tweets CASCADE;
DROP TABLE IF EXISTS stock_sentiment CASCADE;
DROP TABLE IF EXISTS sentiment_logs CASCADE;

-- ============================================
-- 1. TWEETS TABLE (Raw Twitter Data)
-- ============================================
CREATE TABLE tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    author_id VARCHAR(50),
    author_name VARCHAR(100),
    author_followers INTEGER DEFAULT 0,
    
    -- Stock information
    symbol VARCHAR(10) NOT NULL,
    
    -- Sentiment scores
    sentiment_score DECIMAL(4,3),
    sentiment_label VARCHAR(10),
    confidence DECIMAL(4,3),
    
    -- Engagement metrics
    like_count INTEGER DEFAULT 0,
    retweet_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    
    -- Metadata
    source VARCHAR(20) DEFAULT 'twitter',
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_sentiment CHECK (sentiment_label IN ('positive', 'negative', 'neutral', NULL))
);

-- Create indexes for fast queries
CREATE INDEX idx_tweets_symbol ON tweets(symbol);
CREATE INDEX idx_tweets_created ON tweets(created_at DESC);
CREATE INDEX idx_tweets_sentiment ON tweets(sentiment_score);
CREATE INDEX idx_tweets_symbol_created ON tweets(symbol, created_at DESC);

-- ============================================
-- 2. STOCK SENTIMENT AGGREGATES
-- ============================================
CREATE TABLE stock_sentiment (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    time_bucket TIMESTAMP NOT NULL,  -- 1 minute buckets
    avg_sentiment DECIMAL(4,3),
    tweet_volume INTEGER DEFAULT 0,
    positive_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    avg_confidence DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, time_bucket)
);

CREATE INDEX idx_stock_sentiment_symbol_time ON stock_sentiment(symbol, time_bucket DESC);

-- ============================================
-- 3. SENTIMENT LOGS (For debugging)
-- ============================================
CREATE TABLE sentiment_logs (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    symbol VARCHAR(10),
    sentiment_score DECIMAL(4,3),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_logs_created ON sentiment_logs(created_at DESC);

-- ============================================
-- 4. VIEWS FOR EASY QUERYING
-- ============================================

-- Latest sentiment for each stock
CREATE VIEW latest_stock_sentiment AS
SELECT DISTINCT ON (symbol)
    symbol,
    sentiment_score,
    sentiment_label,
    confidence,
    created_at,
    text as sample_tweet
FROM tweets
ORDER BY symbol, created_at DESC;

-- 1-hour summary
CREATE VIEW hourly_summary AS
SELECT 
    symbol,
    date_trunc('hour', created_at) as hour,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(*) as tweet_count,
    AVG(confidence) as avg_confidence
FROM tweets
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY symbol, date_trunc('hour', created_at)
ORDER BY symbol, hour DESC;

-- ============================================
-- COMMENTS
-- ============================================
COMMENT ON TABLE tweets IS 'Raw tweets with sentiment analysis results';
COMMENT ON COLUMN tweets.sentiment_score IS '-1.0 = very negative, 1.0 = very positive';
COMMENT ON COLUMN tweets.confidence IS '0.0 to 1.0, confidence in sentiment prediction';
