"""
Natural Language Understanding Service
Handles intent recognition, entity extraction, and fuzzy matching
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from fuzzywuzzy import fuzz
from textblob import TextBlob


@dataclass
class Intent:
    """Represents a detected user intent"""
    name: str
    confidence: float
    entities: List[Dict[str, str]]


@dataclass
class Entity:
    """Represents an extracted entity"""
    type: str
    value: str
    position: Tuple[int, int]


class NLUService:
    """Natural Language Understanding Service"""
    
    # Intent patterns with keywords
    INTENT_PATTERNS = {
        'ml_question': [
            'how', 'what', 'explain', 'difference', 'vs', 'versus', 
            'neural network', 'cnn', 'rnn', 'lstm', 'transformer',
            'classification', 'regression', 'clustering', 'algorithm'
        ],
        'code_debug': [
            'error', 'bug', 'fix', 'debug', 'not working', 'issue',
            'problem', 'exception', 'traceback', 'fails'
        ],
        'code_generation': [
            'write', 'create', 'generate', 'build', 'make',
            'code for', 'script', 'function', 'class'
        ],
        'explanation': [
            'explain', 'understand', 'clarify', 'elaborate',
            'what is', 'how does', 'why', 'meaning'
        ],
        'dataset_help': [
            'dataset', 'data', 'csv', 'dataframe', 'preprocessing',
            'cleaning', 'null', 'missing values', 'feature engineering'
        ],
        'general_chat': [
            'hello', 'hi', 'hey', 'thanks', 'thank you',
            'good', 'great', 'awesome', 'bye'
        ]
    }
    
    # ML/AI entities to extract
    ML_ENTITIES = [
        'neural network', 'cnn', 'rnn', 'lstm', 'gru', 'transformer',
        'bert', 'gpt', 'random forest', 'xgboost', 'svm', 'knn',
        'linear regression', 'logistic regression', 'decision tree',
        'scikit-learn', 'pytorch', 'tensorflow', 'keras', 'pandas',
        'numpy', 'matplotlib', 'seaborn'
    ]
    
    def __init__(self):
        """Initialize NLU Service"""
        pass
    
    def extract_intent(self, message: str) -> Intent:
        """
        Extract intent from user message
        
        Args:
            message: User's message text
            
        Returns:
            Intent object with name, confidence, and entities
        """
        message_lower = message.lower()
        intent_scores = {}
        
        # Calculate scores for each intent
        for intent_name, keywords in self.INTENT_PATTERNS.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
            
            # Normalize score
            if keywords:
                intent_scores[intent_name] = score / len(keywords)
        
        # Get best matching intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            # Boost confidence if multiple keywords match
            if confidence > 0:
                keyword_matches = sum(1 for kw in self.INTENT_PATTERNS[best_intent] if kw in message_lower)
                confidence = min(1.0, confidence + (keyword_matches * 0.1))
        else:
            best_intent = 'general_chat'
            confidence = 0.3
        
        # Extract entities
        entities = self.extract_entities(message)
        
        return Intent(
            name=best_intent,
            confidence=confidence,
            entities=entities
        )
    
    def extract_entities(self, message: str) -> List[Dict[str, str]]:
        """
        Extract ML/AI entities from message
        
        Args:
            message: User's message text
            
        Returns:
            List of extracted entities
        """
        message_lower = message.lower()
        entities = []
        
        for entity in self.ML_ENTITIES:
            if entity in message_lower:
                pos = message_lower.index(entity)
                entities.append({
                    'type': 'ml_concept',
                    'value': entity,
                    'position': (pos, pos + len(entity))
                })
        
        # Extract programming languages
        prog_langs = ['python', 'r', 'julia', 'java', 'c++']
        for lang in prog_langs:
            if lang in message_lower:
                entities.append({
                    'type': 'programming_language',
                    'value': lang,
                    'position': (0, 0)  # Simplified position
                })
        
        return entities
    
    def handle_typos(self, message: str) -> str:
        """
        Correct common typos using fuzzy matching
        
        Args:
            message: Message that may contain typos
            
        Returns:
            Corrected message
        """
        words = message.split()
        corrected_words = []
        
        # Common ML terms for fuzzy matching
        common_terms = [
            'neural', 'network', 'classification', 'regression',
            'clustering', 'supervised', 'unsupervised', 'reinforcement',
            'learning', 'algorithm', 'model', 'training', 'testing',
            'validation', 'accuracy', 'precision', 'recall'
        ]
        
        for word in words:
            word_lower = word.lower().strip('.,!?')
            
            # Check if word is likely misspelled
            best_match = word
            best_score = 0
            
            for term in common_terms:
                score = fuzz.ratio(word_lower, term)
                if score > best_score and score > 85:  # 85% similarity threshold
                    best_score = score
                    best_match = term
            
            # Preserve original casing and punctuation
            if best_score > 85 and word_lower != best_match:
                # Maintain original punctuation
                for punct in '.,!?':
                    if word.endswith(punct):
                        best_match += punct
                        break
                corrected_words.append(best_match)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def calculate_confidence(self, message: str, predicted_intent: str) -> float:
        """
        Calculate confidence score for intent prediction
        
        Args:
            message: User's message
            predicted_intent: Predicted intent name
            
        Returns:
            Confidence score (0.0 - 1.0)
        """
        message_lower = message.lower()
        
        if predicted_intent not in self.INTENT_PATTERNS:
            return 0.3
        
        # Count matching keywords
        keywords = self.INTENT_PATTERNS[predicted_intent]
        matches = sum(1 for kw in keywords if kw in message_lower)
        
        if not keywords:
            return 0.5
        
        # Base confidence from keyword matches
        base_confidence = matches / len(keywords)
        
        # Boost for exact phrase matches
        exact_matches = sum(1 for kw in keywords if len(kw.split()) > 1 and kw in message_lower)
        boost = exact_matches * 0.15
        
        # Length penalty for very short messages (might be ambiguous)
        if len(message.split()) < 3:
            base_confidence *= 0.8
        
        return min(1.0, base_confidence + boost)
    
    def analyze_question_type(self, message: str) -> Optional[str]:
        """
        Analyze what type of question is being asked
        
        Args:
            message: User's message
            
        Returns:
            Question type or None
        """
        message_lower = message.lower()
        
        question_types = {
            'what': 'definition',
            'how': 'procedure',
            'why': 'explanation',
            'when': 'temporal',
            'where': 'location',
            'which': 'choice',
            'difference between': 'comparison',
            'vs': 'comparison',
            'versus': 'comparison'
        }
        
        for trigger, qtype in question_types.items():
            if trigger in message_lower:
                return qtype
        
        return None


# Singleton instance
nlu_service = NLUService()
