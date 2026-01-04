"""
Database models for conversation storage
Uses SQLAlchemy with SQLite for temporary storage
"""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Conversation(Base):
    """Conversation model for storing chat sessions"""
    __tablename__ = 'conversations'
    
    id = Column(String, primary_key=True)  # Session ID
    user_id = Column(String, default='default')
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    language = Column(String, default='en')
    avg_sentiment = Column(Float, default=0.0)
    message_count = Column(Integer, default=0)

class Message(Base):
    """Message model for storing individual chat messages"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, index=True)
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    intent = Column(String, nullable=True)
    sentiment_emotion = Column(String, nullable=True)
    sentiment_polarity = Column(Float, nullable=True)
    entities = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, nullable=True)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///backend/data/moonknight.db')

def get_engine():
    """Get database engine"""
    # Create data directory if it doesn't exist
    os.makedirs('backend/data', exist_ok=True)
    return create_engine(DATABASE_URL, echo=False)

def init_database():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

def get_session():
    """Get database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Initialize database on module load
init_database()
