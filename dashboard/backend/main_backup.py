from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import random

# Create FastAPI app
app = FastAPI(
    title="Stock Sentiment API",
    description="Real-time stock sentiment analysis from Twitter",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
stocks = ["TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA"]
sentiments = ["positive", "negative", "neutral"]

# ----- BASIC ENDPOINTS -----
@app.get("/")
async def root():
    return {
        "message": "🚀 Stock Sentiment API is running!",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": "uvicorn",
        "port": 8000
    }

@app.get("/api/test")
async def test():
    """Test endpoint"""
    return {"message": "API is working!", "success": True}

# ----- STOCK ENDPOINTS -----
@app.get("/api/stocks")
async def get_stocks():
    """Get list of tracked stocks"""
    return {
        "stocks": stocks,
        "count": len(stocks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/sentiment/{symbol}")
async def get_stock_sentiment(symbol: str):
    """Get current sentiment for a specific stock"""
    symbol = symbol.upper()
    if symbol not in stocks:
        return {"error": f"Stock {symbol} not tracked", "available": stocks}
    
    return {
        "symbol": symbol,
        "sentiment": random.choice(sentiments),
        "score": round(random.uniform(-1, 1), 2),
        "confidence": round(random.uniform(0.5, 0.95), 2),
        "tweet_volume": random.randint(100, 5000),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard")
async def get_dashboard():
    """Get sentiment dashboard for all stocks"""
    data = []
    for stock in stocks:
        data.append({
            "symbol": stock,
            "sentiment": random.choice(sentiments),
            "score": round(random.uniform(-1, 1), 2),
            "volume": random.randint(100, 5000),
            "change": round(random.uniform(-5, 5), 2)
        })
    
    # Calculate overall market sentiment
    positive_count = sum(1 for d in data if d['sentiment'] == 'positive')
    negative_count = sum(1 for d in data if d['sentiment'] == 'negative')
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_stocks": len(stocks),
        "market_sentiment": {
            "positive": positive_count,
            "negative": negative_count,
            "neutral": len(stocks) - positive_count - negative_count
        },
        "data": data
    }

# ----- WEBSOCKET FOR REAL-TIME -----
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ----- RUN SERVER -----
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STOCK SENTIMENT API SERVER")
    print("=" * 60)
    print(f"\n📊 Tracking {len(stocks)} stocks:")
    print(f"   {', '.join(stocks)}")
    print(f"\n🌐 Endpoints:")
    print(f"   📍 http://localhost:8000/")
    print(f"   📍 http://localhost:8000/health")
    print(f"   📍 http://localhost:8000/api/stocks")
    print(f"   📍 http://localhost:8000/api/sentiment/TSLA")
    print(f"   📍 http://localhost:8000/api/dashboard")
    print(f"   📍 http://localhost:8000/docs")
    print(f"\n✅ Server starting...")
    print("=" * 60)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
