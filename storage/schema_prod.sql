-- ============================================
-- PROFESSIONAL STOCK SENTIMENT DATABASE
-- ============================================

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    role VARCHAR(20) DEFAULT 'user'
);

-- API keys for external access
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    api_key VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Tweets table (your existing one enhanced)
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    author_id VARCHAR(50),
    author_name VARCHAR(100),
    author_followers INTEGER DEFAULT 0,
    author_verified BOOLEAN DEFAULT false,
    
    -- Stock information
    symbol VARCHAR(10) NOT NULL,
    
    -- Sentiment scores (multiple models)
    sentiment_vader DECIMAL(4,3),
    sentiment_textblob DECIMAL(4,3),
    sentiment_finbert DECIMAL(4,3),
    sentiment_final DECIMAL(4,3),
    sentiment_label VARCHAR(10),
    confidence DECIMAL(4,3),
    
    -- Engagement metrics
    like_count INTEGER DEFAULT 0,
    retweet_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    impression_count INTEGER DEFAULT 0,
    
    -- Metadata
    source VARCHAR(20) DEFAULT 'twitter',
    language VARCHAR(10) DEFAULT 'en',
    collected_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT valid_sentiment CHECK (sentiment_label IN ('positive', 'negative', 'neutral', NULL))
);

-- Time-series aggregated data
CREATE TABLE IF NOT EXISTS sentiment_aggregates (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    bucket_minute TIMESTAMP NOT NULL,
    avg_sentiment DECIMAL(4,3),
    tweet_count INTEGER,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,
    volume_weighted_sentiment DECIMAL(4,3),
    volatility DECIMAL(4,3),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, bucket_minute)
);

-- Trading signals
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    signal_type VARCHAR(20),
    signal_strength DECIMAL(4,3),
    confidence DECIMAL(4,3),
    triggered_at TIMESTAMP NOT NULL,
    sentiment_score DECIMAL(4,3),
    price_at_signal DECIMAL(10,2),
    price_change_1h DECIMAL(5,2),
    metadata JSONB,
    is_active BOOLEAN DEFAULT true
);

-- Alerts for users
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    symbol VARCHAR(10),
    alert_type VARCHAR(20),
    threshold DECIMAL(4,3),
    message TEXT,
    triggered_at TIMESTAMP,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance monitoring
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100),
    response_time_ms INTEGER,
    status_code INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_tweets_symbol_created ON tweets(symbol, created_at DESC);
CREATE INDEX idx_tweets_sentiment ON tweets(sentiment_final);
CREATE INDEX idx_aggregates_symbol_time ON sentiment_aggregates(symbol, bucket_minute DESC);
CREATE INDEX idx_signals_symbol_time ON trading_signals(symbol, triggered_at DESC);
CREATE INDEX idx_alerts_user_read ON alerts(user_id, is_read);
CREATE INDEX idx_performance_time ON performance_metrics(timestamp);

-- Create views for common queries
CREATE VIEW latest_sentiment AS
SELECT DISTINCT ON (symbol)
    symbol,
    sentiment_final as sentiment,
    sentiment_label,
    confidence,
    created_at,
    text as sample_tweet
FROM tweets
ORDER BY symbol, created_at DESC;

CREATE VIEW hourly_summary AS
SELECT 
    symbol,
    date_trunc('hour', created_at) as hour,
    AVG(sentiment_final) as avg_sentiment,
    COUNT(*) as tweet_count,
    SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) as positive,
    SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) as negative
FROM tweets
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY symbol, date_trunc('hour', created_at);

-- Comments for documentation
COMMENT ON TABLE tweets IS 'Raw tweets with multi-model sentiment analysis';
COMMENT ON TABLE sentiment_aggregates IS 'Time-series aggregated sentiment data';
COMMENT ON TABLE trading_signals IS 'AI-generated trading signals based on sentiment';
COMMENT ON TABLE alerts IS 'User alerts for sentiment thresholds';
