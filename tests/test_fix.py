import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from services.translation_service import translation_service
from services.sentiment_service import sentiment_service

def test_translation_with_code():
    print("\n--- Testing Translation with Code Blocks ---")
    text = "Here is a Python function:\n\n```python\ndef hello():\n    print('Hello World')\n```\nHope this helps!"
    
    # Test Spanish
    translated_es = translation_service.translate(text, 'es')
    print(f"Spanish Translation:\n{translated_es}")
    assert "def hello():" in translated_es
    assert "print('Hello World')" in translated_es
    assert "```python" in translated_es
    
    # Test Tamil
    translated_ta = translation_service.translate(text, 'ta')
    print(f"\nTamil Translation:\n{translated_ta}")
    assert "def hello():" in translated_ta
    assert "```python" in translated_ta
    print("Code blocks preserved in Tamil.")

def test_multi_lingual_sentiment():
    print("\n--- Testing Multi-lingual Sentiment Analysis ---")
    
    # English (Positive)
    s_en = sentiment_service.analyze_sentiment("I love this assistant, it's great!")
    print(f"English Sentiment: {s_en.emotion} (Polarity: {s_en.polarity})")
    assert s_en.polarity > 0
    
    # Tamil (Positive - "I am very happy")
    s_ta = sentiment_service.analyze_sentiment("நான் மிகவும் மகிழ்ச்சியாக இருக்கிறேன்")
    print(f"Tamil Sentiment: {s_ta.emotion} (Polarity: {s_ta.polarity})")
    assert s_ta.polarity > 0
    
    # Hindi (Negative - "This is not working, I am frustrated")
    s_hi = sentiment_service.analyze_sentiment("यह काम नहीं कर रहा है, मैं निराश हूँ")
    print(f"Hindi Sentiment: {s_hi.emotion} (Polarity: {s_hi.polarity})")
    assert s_hi.emotion == 'frustrated' or s_hi.polarity < 0

if __name__ == "__main__":
    try:
        test_translation_with_code()
        test_multi_lingual_sentiment()
        print("\n✅ All backend tests passed!")
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
