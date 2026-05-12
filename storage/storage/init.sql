-- Create database schema
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) UNIQUE,
    text TEXT NOT NULL,
    created_at TIMESTAMP,
    author_id VARCHAR(50),
    source VARCHAR(20),
    symbols TEXT[],
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sentiment (
    id SERIAL PRIMARY KEY,
    tweet_id INTEGER REFERENCES tweets(id),
    polarity DECIMAL(3,2),
    subjectivity DECIMAL(3,2),
    sentiment VARCHAR(10),
    confidence DECIMAL(3,2),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock_sentiment_daily (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10),
    date DATE,
    avg_polarity DECIMAL(4,3),
    total_tweets INTEGER,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_tweets_symbols ON tweets USING gin(symbols);
CREATE INDEX idx_tweets_created ON tweets(created_at);
CREATE INDEX idx_sentiment_tweet ON sentiment(tweet_id);
CREATE INDEX idx_stock_daily ON stock_sentiment_daily(symbol, date);