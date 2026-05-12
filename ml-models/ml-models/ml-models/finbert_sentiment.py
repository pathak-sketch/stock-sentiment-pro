# ml-models/finbert_sentiment.py
from transformers import pipeline
import torch
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FinBertSentimentAnalyzer:
    """Advanced sentiment analyzer using FinBERT"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        logger.info(f"Loading {model_name}...")
        self.classifier = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("Model loaded successfully")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze financial sentiment"""
        try:
            result = self.classifier(text)[0]
            
            # Map labels to our format
            label_map = {
                'positive': 'positive',
                'negative': 'negative',
                'neutral': 'neutral'
            }
            
            return {
                'sentiment': label_map.get(result['label'], 'neutral'),
                'confidence': round(result['score'], 3),
                'model': 'finbert'
            }
            
        except Exception as e:
            logger.error(f"FinBERT error: {e}")
            # Fall back to TextBlob
            from simple_sentiment import SimpleSentimentAnalyzer
            fallback = SimpleSentimentAnalyzer()
            return fallback.analyze(text)

# Test both analyzers
if __name__ == "__main__":
    print("Testing sentiment analyzers...")
    
    # Simple analyzer
    simple = SimpleSentimentAnalyzer()
    
    # FinBERT (will download ~500MB on first run)
    try:
        finbert = FinBertSentimentAnalyzer()
        use_finbert = True
        print("✅ FinBERT loaded successfully")
    except:
        use_finbert = False
        print("⚠️ FinBERT not available, using TextBlob only")
    
    test_cases = [
        "Tesla stock is soaring after earnings beat",
        "Apple faces regulatory challenges in EU",
        "Microsoft cloud revenue grows 25%",
        "Market crash expected due to inflation"
    ]
    
    for text in test_cases:
        print(f"\n📝 Text: {text}")
        
        # Simple analysis
        simple_result = simple.analyze(text)
        print(f"   TextBlob: {simple_result['sentiment']} ({simple_result['polarity']})")
        
        # FinBERT if available
        if use_finbert:
            finbert_result = finbert.analyze(text)
            print(f"   FinBERT: {finbert_result['sentiment']} ({finbert_result['confidence']})")