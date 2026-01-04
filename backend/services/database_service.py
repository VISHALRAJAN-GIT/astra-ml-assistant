"""
Database service for managing conversations in SQLite
"""
from models.database import get_session, Conversation, Message
from datetime import datetime
from typing import List, Dict, Optional


class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def save_conversation(self, conversation_id: str, title: str, language: str = 'en'):
        """Save or update conversation"""
        conv = self.session.query(Conversation).filter_by(id=conversation_id).first()
        
        if not conv:
            conv = Conversation(
                id=conversation_id,
                title=title,
                language=language,
                created_at=datetime.utcnow()
            )
            self.session.add(conv)
        else:
            conv.title = title
            conv.language = language
            conv.updated_at = datetime.utcnow()
        
        self.session.commit()
        return conv
    
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        intent: Optional[str] = None,
        sentiment_emotion: Optional[str] = None,
        sentiment_polarity: Optional[float] = None,
        entities: Optional[List[Dict]] = None,
        confidence: Optional[float] = None
    ):
        """Save a message to the database"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            intent=intent,
            sentiment_emotion=sentiment_emotion,
            sentiment_polarity=sentiment_polarity,
            entities=entities,
            confidence=confidence,
            timestamp=datetime.utcnow()
        )
        
        self.session.add(message)
        
        # Update conversation message count and average sentiment
        conv = self.session.query(Conversation).filter_by(id=conversation_id).first()
        if conv:
            conv.message_count += 1
            conv.updated_at = datetime.utcnow()
            
            # Update average sentiment if this is a user message
            if role == 'user' and sentiment_polarity is not None:
                messages = self.session.query(Message).filter_by(
                    conversation_id=conversation_id,
                    role='user'
                ).all()
                
                total_polarity = sum(m.sentiment_polarity for m in messages if m.sentiment_polarity)
                conv.avg_sentiment = total_polarity / len(messages) if messages else 0.0
        
        self.session.commit()
        return message
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        return self.session.query(Conversation).filter_by(id=conversation_id).first()
    
    def get_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        """Get messages for a conversation"""
        return self.session.query(Message).filter_by(
            conversation_id=conversation_id
        ).order_by(Message.timestamp.desc()).limit(limit).all()
    
    def get_recent_conversations(self, limit: int = 20) -> List[Conversation]:
        """Get recent conversations"""
        return self.session.query(Conversation).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).all()
    
    def delete_conversation(self, conversation_id: str):
        """Delete a conversation and its messages"""
        self.session.query(Message).filter_by(conversation_id=conversation_id).delete()
        self.session.query(Conversation).filter_by(id=conversation_id).delete()
        self.session.commit()
    
    def delete_old_conversations(self, days: int = 7):
        """Delete conversations older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_convs = self.session.query(Conversation).filter(
            Conversation.updated_at < cutoff_date
        ).all()
        
        for conv in old_convs:
            self.delete_conversation(conv.id)
        
        return len(old_convs)
    
    def get_analytics(self, conversation_id: str) -> Dict:
        """Get analytics for a conversation"""
        conv = self.get_conversation(conversation_id)
        messages = self.get_messages(conversation_id, limit=1000)
        
        if not conv:
            return {}
        
        user_messages = [m for m in messages if m.role == 'user']
        
        # Intent distribution
        intents = {}
        for msg in user_messages:
            if msg.intent:
                intents[msg.intent] = intents.get(msg.intent, 0) + 1
        
        # Emotion distribution
        emotions = {}
        for msg in user_messages:
            if msg.sentiment_emotion:
                emotions[msg.sentiment_emotion] = emotions.get(msg.sentiment_emotion, 0) + 1
        
        return {
            'conversation_id': conversation_id,
            'title': conv.title,
            'message_count': conv.message_count,
            'avg_sentiment': conv.avg_sentiment,
            'created_at': conv.created_at.isoformat(),
            'updated_at': conv.updated_at.isoformat(),
            'intent_distribution': intents,
            'emotion_distribution': emotions,
            'user_message_count': len(user_messages)
        }


# Singleton instance
db_service = DatabaseService()
