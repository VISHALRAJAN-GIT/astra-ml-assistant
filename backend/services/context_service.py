"""
Context Management Service
Manages conversation context and memory across sessions
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Message:
    """Represents a conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str
    intent: Optional[str] = None
    sentiment: Optional[Dict] = None
    entities: Optional[List[Dict]] = None


@dataclass
class ConversationContext:
    """Represents conversation context"""
    session_id: str
    messages: List[Message]
    user_preferences: Dict
    topic: Optional[str] = None
    last_entities: List[Dict] = None
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'messages': [asdict(m) for m in self.messages],
            'user_preferences': self.user_preferences,
            'topic': self.topic,
            'last_entities': self.last_entities or []
        }


class ContextService:
    """Context Management Service"""
    
    def __init__(self, storage_path: str = "backend/data/contexts.json"):
        """
        Initialize Context Service
        
        Args:
            storage_path: Path to store context data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(exist_ok=True)
        self.contexts: Dict[str, ConversationContext] = {}
        self._load_contexts()
    
    def _load_contexts(self):
        """Load contexts from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_id, ctx_data in data.items():
                        messages = [Message(**m) for m in ctx_data.get('messages', [])]
                        self.contexts[session_id] = ConversationContext(
                            session_id=session_id,
                            messages=messages,
                            user_preferences=ctx_data.get('user_preferences', {}),
                            topic=ctx_data.get('topic'),
                            last_entities=ctx_data.get('last_entities', [])
                        )
            except Exception as e:
                print(f"Error loading contexts: {e}")
    
    def _save_contexts(self):
        """Save contexts to storage"""
        try:
            data = {sid: ctx.to_dict() for sid, ctx in self.contexts.items()}
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving contexts: {e}")
    
    def get_conversation_context(self, session_id: str) -> ConversationContext:
        """
        Get conversation context for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationContext object
        """
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(
                session_id=session_id,
                messages=[],
                user_preferences={},
                topic=None,
                last_entities=[]
            )
        return self.contexts[session_id]
    
    def update_context(
        self,
        session_id: str,
        message: Message,
        intent: Optional[str] = None,
        entities: Optional[List[Dict]] = None
    ):
        """
        Update conversation context with new message
        
        Args:
            session_id: Session identifier
            message: Message to add
            intent: Detected intent
            entities: Extracted entities
        """
        context = self.get_conversation_context(session_id)
        
        # Update message with metadata
        message.intent = intent
        message.entities = entities
        
        # Add message to context
        context.messages.append(message)
        
        # Update last entities
        if entities:
            context.last_entities = entities
        
        # Detect and update topic
        if intent:
            context.topic = self._detect_topic(context.messages[-5:])  # Last 5 messages
        
        # Keep only last 50 messages to prevent memory overflow
        if len(context.messages) > 50:
            context.messages = context.messages[-50:]
        
        # Save to storage
        self._save_contexts()
    
    def _detect_topic(self, recent_messages: List[Message]) -> Optional[str]:
        """
        Detect conversation topic from recent messages
        
        Args:
            recent_messages: Recent messages
            
        Returns:
            Detected topic
        """
        # Count entity types
        entity_types = {}
        for msg in recent_messages:
            if msg.entities:
                for entity in msg.entities:
                    etype = entity.get('type')
                    if etype:
                        entity_types[etype] = entity_types.get(etype, 0) + 1
        
        # Most common entity type is likely the topic
        if entity_types:
            topic = max(entity_types, key=entity_types.get)
            return topic
        
        return None
    
    def get_relevant_context(self, query: str, session_id: str, max_messages: int = 5) -> str:
        """
        Get relevant context for a query
        
        Args:
            query: User's query
            session_id: Session identifier
            max_messages: Maximum messages to include
            
        Returns:
            Relevant context as string
        """
        context = self.get_conversation_context(session_id)
        
        if not context.messages:
            return ""
        
        # Get recent messages
        recent = context.messages[-max_messages:]
        
        # Format context
        context_str = "Previous conversation:\n"
        for msg in recent:
            role = "User" if msg.role == "user" else "Assistant"
            context_str += f"{role}: {msg.content[:100]}...\n"
        
        # Add topic if exists
        if context.topic:
            context_str += f"\nCurrent topic: {context.topic}\n"
        
        return context_str
    
    def summarize_history(self, session_id: str) -> str:
        """
        Summarize conversation history
        
        Args:
            session_id: Session identifier
            
        Returns:
            Summary of conversation
        """
        context = self.get_conversation_context(session_id)
        
        if not context.messages:
            return "No conversation history"
        
        user_messages = [m for m in context.messages if m.role == "user"]
        
        # Collect topics discussed
        topics = set()
        for msg in user_messages:
            if msg.intent:
                topics.add(msg.intent)
        
        summary = f"Conversation Summary:\n"
        summary += f"- Total messages: {len(context.messages)}\n"
        summary += f"- User messages: {len(user_messages)}\n"
        summary += f"- Topics discussed: {', '.join(topics) if topics else 'General chat'}\n"
        
        if context.topic:
            summary += f"- Current focus: {context.topic}\n"
        
        return summary
    
    def clear_context(self, session_id: str):
        """
        Clear context for a session
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.contexts:
            del self.contexts[session_id]
            self._save_contexts()
    
    def get_user_preferences(self, session_id: str) -> Dict:
        """
        Get user preferences for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            User preferences dictionary
        """
        context = self.get_conversation_context(session_id)
        return context.user_preferences
    
    def update_user_preferences(self, session_id: str, preferences: Dict):
        """
        Update user preferences
        
        Args:
            session_id: Session identifier
            preferences: Preferences to update
        """
        context = self.get_conversation_context(session_id)
        context.user_preferences.update(preferences)
        self._save_contexts()


# Singleton instance
context_service = ContextService()
