from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import database
try:
    from storage.sqlite_handler import db
    DATABASE_AVAILABLE = True
    print("✅ Database connected - SQLite")
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️ Database not available: {e}")

app = FastAPI(
    title="Stock Sentiment API",
    description="Professional Stock Sentiment Analysis Platform",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Stock data
stocks = ["TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA"]
sentiments = ["positive", "negative", "neutral"]

@app.get("/")
async def root():
    return {
        "message": "🚀 Stock Sentiment API is running!",
        "version": "2.0.0",
        "status": "online",
        "database": "connected" if DATABASE_AVAILABLE else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected" if DATABASE_AVAILABLE else "disconnected",
        "stocks_tracked": len(stocks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stocks")
async def get_stocks():
    """Get list of tracked stocks with latest sentiment"""
    stocks_data = []
    
    if DATABASE_AVAILABLE:
        for stock in stocks:
            summary = db.get_sentiment_summary(stock, 1)  # Last 1 hour
            stocks_data.append({
                "symbol": stock,
                "sentiment": summary.get('avg_sentiment', 0),
                "tweet_volume": summary.get('total_tweets', 0),
                "positive_ratio": summary.get('positive_pct', 0)
            })
    else:
        # Mock data if no database
        for stock in stocks:
            stocks_data.append({
                "symbol": stock,
                "sentiment": round(random.uniform(-1, 1), 2),
                "tweet_volume": random.randint(100, 5000),
                "positive_ratio": round(random.uniform(0, 100), 2)
            })
    
    return {
        "stocks": stocks,
        "count": len(stocks),
        "data": stocks_data,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sentiment/{symbol}")
async def get_stock_sentiment(symbol: str):
    """Get detailed sentiment for a specific stock"""
    symbol = symbol.upper()
    
    if symbol not in stocks:
        return {"error": f"Stock {symbol} not tracked", "available": stocks}
    
    if DATABASE_AVAILABLE:
        summary = db.get_sentiment_summary(symbol, 24)
        recent = db.get_recent_sentiment(symbol, 5)
        
        return {
            "symbol": symbol,
            "summary": {
                "avg_sentiment": round(summary.get('avg_sentiment', 0), 3),
                "total_tweets": summary.get('total_tweets', 0),
                "positive": summary.get('positive_count', 0),
                "negative": summary.get('negative_count', 0),
                "neutral": summary.get('neutral_count', 0),
                "positive_ratio": summary.get('positive_pct', 0),
                "negative_ratio": summary.get('negative_pct', 0),
                "confidence": round(summary.get('avg_confidence', 0), 3)
            },
            "recent_tweets": recent[:3] if recent else [],
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Mock data
        sentiment = random.choice(sentiments)
        score = round(random.uniform(-1, 1), 2)
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": score,
            "confidence": round(random.uniform(0.5, 0.95), 2),
            "tweet_volume": random.randint(100, 5000),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/dashboard")
async def get_dashboard():
    """Get complete dashboard data"""
    if DATABASE_AVAILABLE:
        market_data = db.get_market_summary()
    else:
        market_data = []
        for stock in stocks:
            market_data.append({
                "symbol": stock,
                "avg_sentiment": round(random.uniform(-1, 1), 2),
                "tweet_volume": random.randint(100, 5000),
                "last_update": datetime.now().isoformat()
            })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "market_sentiment": market_data,
        "total_stocks": len(stocks),
        "database_status": "connected" if DATABASE_AVAILABLE else "disconnected"
    }

@app.get("/api/history/{symbol}")
async def get_sentiment_history(symbol: str, hours: int = 24):
    """Get historical sentiment data for charts"""
    symbol = symbol.upper()
    
    if DATABASE_AVAILABLE:
        # This would normally come from database
        # For now, generate mock historical data
        import random
        from datetime import timedelta
        
        history = []
        now = datetime.now()
        
        for i in range(hours):
            time = now - timedelta(hours=hours-i)
            history.append({
                "time": time.isoformat(),
                "sentiment": round(random.uniform(-0.8, 0.8), 2),
                "volume": random.randint(50, 500)
            })
        
        return {
            "symbol": symbol,
            "history": history,
            "timestamp": now.isoformat()
        }
    else:
        return {"error": "Database not connected"}

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STOCK SENTIMENT API v2.0")
    print("=" * 60)
    print(f"\n📊 Tracking {len(stocks)} stocks:")
    print(f"   {', '.join(stocks)}")
    print(f"\n💾 Database: {'✅ SQLite connected' if DATABASE_AVAILABLE else '⚠️ Not connected'}")
    print(f"\n🌐 Endpoints:")
    print(f"   📍 http://localhost:8000/")
    print(f"   📍 http://localhost:8000/docs")
    print(f"   📍 http://localhost:8000/api/stocks")
    print(f"   📍 http://localhost:8000/api/sentiment/TSLA")
    print(f"   📍 http://localhost:8000/api/dashboard")
    print("\n" + "=" * 60)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
