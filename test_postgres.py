import asyncio
import asyncpg

async def init_db():
    # Connect
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password123',
        database='stock_sentiment'
    )
    
    # Create table
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS test (
            id SERIAL PRIMARY KEY,
            message TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    # Insert test data
    await conn.execute(
        'INSERT INTO test (message) VALUES ($1)',
        'Hello from Python!'
    )
    
    # Query data
    rows = await conn.fetch('SELECT * FROM test')
    for row in rows:
        print(f"ID: {row['id']}, Message: {row['message']}, Time: {row['created_at']}")
    
    await conn.close()
    print("\n✅ Database test complete!")

asyncio.run(init_db())
