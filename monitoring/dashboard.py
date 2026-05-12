# monitoring/dashboard.py
import logging
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from storage.db_client import DatabaseClient

async def generate_report():
    """Generate daily report"""
    db = DatabaseClient()
    await db.connect()
    
    # Get data for all symbols
    symbols = ['TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN']
    
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'summary': {}
    }
    
    for symbol in symbols:
        data = await db.get_daily_sentiment(symbol, 1)
        if data:
            latest = data[0]
            report['summary'][symbol] = {
                'sentiment': latest['avg_polarity'],
                'tweets': latest['total_tweets'],
                'positive_ratio': latest['positive_count'] / latest['total_tweets'] if latest['total_tweets'] > 0 else 0
            }
    
    # Create visualization
    df = pd.DataFrame.from_dict(report['summary'], orient='index')
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Sentiment bar chart
    df['sentiment'].plot(kind='bar', ax=axes[0], color='skyblue')
    axes[0].set_title('Sentiment by Stock')
    axes[0].set_ylabel('Sentiment Score')
    axes[0].axhline(y=0, color='r', linestyle='-', alpha=0.3)
    
    # Tweet volume
    df['tweets'].plot(kind='bar', ax=axes[1], color='lightgreen')
    axes[1].set_title('Tweet Volume by Stock')
    axes[1].set_ylabel('Number of Tweets')
    
    plt.tight_layout()
    plt.savefig('daily_report.png')
    plt.close()
    
    return report

if __name__ == "__main__":
    import asyncio
    report = asyncio.run(generate_report())
    print("📊 Daily Report:")
    print(json.dumps(report, indent=2))