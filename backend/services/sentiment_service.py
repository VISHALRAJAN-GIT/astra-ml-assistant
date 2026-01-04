"""
Sentiment Analysis Service
Analyzes user emotions and adjusts bot responses accordingly
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from textblob import TextBlob
import re


@dataclass
class SentimentScore:
    """Sentiment analysis result"""
    polarity: float  # -1 (negative) to 1 (positive)
    subjectivity: float  # 0 (objective) to 1 (subjective)
    emotion: str  # frustrated, satisfied, neutral, urgent, confused
    confidence: float


class SentimentService:
    """Sentiment Analysis Service"""
    
    # Emotion indicators
    FRUSTRATION_INDICATORS = [
        'not working', 'doesn\'t work', 'broken', 'frustrated', 'annoying',
        'stupid', 'terrible', 'awful', 'useless', 'waste', 'failed',
        'error', 'wrong', 'bad', 'hate', 'worst', 'can\'t', 'unable'
    ]
    
    SATISFACTION_INDICATORS = [
        'thanks', 'thank you', 'great', 'awesome', 'excellent', 'perfect',
        'amazing', 'wonderful', 'love', 'helpful', 'good', 'nice',
        'appreciate', 'brilliant', 'fantastic'
    ]
    
    URGENCY_INDICATORS = [
        'urgent', 'asap', 'immediately', 'quickly', 'now', 'emergency',
        'critical', 'deadline', 'hurry', 'fast', 'soon', 'right now'
    ]
    
    CONFUSION_INDICATORS = [
        'confused', 'don\'t understand', 'unclear', 'what do you mean',
        'explain', 'clarify', 'lost', 'stuck', 'help', 'how to'
    ]
    
    def __init__(self):
        """Initialize Sentiment Service"""
        self.escalation_threshold = -0.5  # Polarity below this triggers escalation
        self.consecutive_negative_count = 0
    
    def analyze_sentiment(self, message: str) -> SentimentScore:
        """
        Analyze sentiment of user message. 
        Supports multi-lingual input by translating to English first.
        
        Args:
            message: User's message text
            
        Returns:
            SentimentScore with polarity, emotion, and confidence
        """
        # Detect language and translate to English if necessary
        from services.translation_service import translation_service
        lang = translation_service.detect_language(message)
        
        analysis_text = message
        if lang != 'en':
            analysis_text = translation_service.translate(message, 'en', lang)
            print(f"Sentiment Analysis: Translated '{lang}' to English for analysis: {analysis_text}")

        # Use TextBlob for base sentiment analysis
        blob = TextBlob(analysis_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Detect specific emotions
        emotion = self._detect_emotion(analysis_text, polarity)
        
        # Calculate confidence based on subjectivity and text length
        confidence = min(1.0, (subjectivity + 0.3) * (len(analysis_text.split()) / 10))
        confidence = max(0.3, min(0.95, confidence))
        
        return SentimentScore(
            polarity=polarity,
            subjectivity=subjectivity,
            emotion=emotion,
            confidence=confidence
        )
    
    def _detect_emotion(self, message: str, polarity: float) -> str:
        """
        Detect specific emotion from message
        
        Args:
            message: User's message
            polarity: Sentiment polarity score
            
        Returns:
            Emotion name
        """
        message_lower = message.lower()
        
        # Check for urgency first (highest priority)
        if any(indicator in message_lower for indicator in self.URGENCY_INDICATORS):
            return 'urgent'
        
        # Check for frustration
        frustration_count = sum(1 for ind in self.FRUSTRATION_INDICATORS if ind in message_lower)
        if frustration_count >= 2 or polarity < -0.3:
            return 'frustrated'
        
        # Check for satisfaction
        if any(indicator in message_lower for indicator in self.SATISFACTION_INDICATORS):
            return 'satisfied'
        
        # Check for confusion
        if any(indicator in message_lower for indicator in self.CONFUSION_INDICATORS):
            return 'confused'
        
        # Default based on polarity
        if polarity > 0.3:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def detect_frustration(self, message: str) -> bool:
        """
        Detect if user is frustrated
        
        Args:
            message: User's message
            
        Returns:
            True if frustration detected
        """
        sentiment = self.analyze_sentiment(message)
        return sentiment.emotion in ['frustrated', 'angry']
    
    def adjust_tone(self, response: str, sentiment: SentimentScore) -> str:
        """
        Adjust response tone based on user sentiment
        
        Args:
            response: Bot's response
            sentiment: User's sentiment
            
        Returns:
            Tone-adjusted response
        """
        emotion = sentiment.emotion
        
        # Prefix based on emotion
        prefixes = {
            'frustrated': "I understand this can be frustrating. Let me help you sort this out.\n\n",
            'confused': "No worries, let me break this down clearly for you.\n\n",
            'urgent': "I see this is time-sensitive. Here's a quick solution:\n\n",
            'satisfied': "Glad I could help! ",
            'positive': "",
            'negative': "I'm here to help. ",
            'neutral': ""
        }
        
        prefix = prefixes.get(emotion, "")
        
        # Add empathetic suffix for negative emotions
        if emotion in ['frustrated', 'confused', 'negative']:
            # Check if response is long enough to add a supportive message
            if len(response) > 100:
                suffix = "\n\n💡 Feel free to ask if you need more clarification!"
                return prefix + response + suffix
        
        return prefix + response
    
    def should_escalate(self, conversation_history: List[Dict]) -> bool:
        """
        Determine if conversation should be escalated to human
        
        Args:
            conversation_history: List of messages with sentiment
            
        Returns:
            True if escalation recommended
        """
        if len(conversation_history) < 2:
            return False
        
        # Check recent messages
        recent_messages = conversation_history[-5:]  # Last 5 messages
        
        # Count consecutive negative sentiments
        consecutive_negative = 0
        for msg in reversed(recent_messages):
            if msg.get('role') == 'user':
                sentiment = msg.get('sentiment', {})
                if sentiment.get('emotion') in ['frustrated', 'angry', 'negative']:
                    consecutive_negative += 1
                else:
                    break
        
        # Escalate if 3+ consecutive negative messages
        if consecutive_negative >= 3:
            return True
        
        # Check for explicit escalation requests
        last_user_message = next((msg for msg in reversed(recent_messages) if msg.get('role') == 'user'), None)
        if last_user_message:
            message_lower = last_user_message.get('content', '').lower()
            escalation_phrases = [
                'talk to human', 'speak to person', 'real person',
                'human agent', 'customer service', 'representative',
                'not helpful', 'this isn\'t working'
            ]
            if any(phrase in message_lower for phrase in escalation_phrases):
                return True
        
        return False
    
    def get_sentiment_emoji(self, emotion: str) -> str:
        """
        Get emoji representation of emotion
        
        Args:
            emotion: Emotion name
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'frustrated': '😤',
            'satisfied': '😊',
            'positive': '🙂',
            'negative': '😟',
            'neutral': '😐',
            'urgent': '⚡',
            'confused': '🤔',
            'angry': '😠'
        }
        return emoji_map.get(emotion, '😐')
    
    def get_sentiment_summary(self, conversation_history: List[Dict]) -> Dict:
        """
        Get overall sentiment summary of conversation
        
        Args:
            conversation_history: List of messages
            
        Returns:
            Summary with average sentiment and trend
        """
        if not conversation_history:
            return {'average_polarity': 0, 'trend': 'neutral', 'total_messages': 0}
        
        user_messages = [msg for msg in conversation_history if msg.get('role') == 'user']
        
        if not user_messages:
            return {'average_polarity': 0, 'trend': 'neutral', 'total_messages': 0}
        
        # Calculate average polarity
        polarities = [msg.get('sentiment', {}).get('polarity', 0) for msg in user_messages]
        avg_polarity = sum(polarities) / len(polarities) if polarities else 0
        
        # Determine trend (comparing first half to second half)
        mid = len(polarities) // 2
        if mid > 0:
            first_half_avg = sum(polarities[:mid]) / mid
            second_half_avg = sum(polarities[mid:]) / (len(polarities) - mid)
            
            if second_half_avg > first_half_avg + 0.1:
                trend = 'improving'
            elif second_half_avg < first_half_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'neutral'
        
        return {
            'average_polarity': avg_polarity,
            'trend': trend,
            'total_messages': len(user_messages),
            'last_emotion': user_messages[-1].get('sentiment', {}).get('emotion', 'neutral')
        }


# Singleton instance
sentiment_service = SentimentService()
