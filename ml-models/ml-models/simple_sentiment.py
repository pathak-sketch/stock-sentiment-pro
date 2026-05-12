# ml-models/simple_sentiment.py
from textblob import TextBlob
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SimpleSentimentAnalyzer:
    """Simple sentiment analyzer using TextBlob"""
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Returns:
        {
            'polarity': -1 to 1 (negative to positive),
            'subjectivity': 0 to 1 (objective to subjective),
            'sentiment': 'positive', 'negative', or 'neutral'
        }
        """
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment label
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'sentiment': sentiment,
                'confidence': round(abs(polarity), 3)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {
                'polarity': 0,
                'subjectivity': 0.5,
                'sentiment': 'neutral',
                'confidence': 0,
                'error': str(e)
            }
    
    def analyze_batch(self, texts: list) -> list:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]

# Test it
if __name__ == "__main__":
    analyzer = SimpleSentimentAnalyzer()
    
    test_texts = [
        "Tesla stock is going to the moon! 🚀",
        "I'm selling all my Apple shares, terrible earnings",
        "Microsoft announced quarterly results today",
        "This is the worst investment ever",
        "Amazing growth by Amazon this quarter"
    ]
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"📊 Text: {text[:50]}...")
        print(f"   Sentiment: {result['sentiment']} (Score: {result['polarity']})")
        print()