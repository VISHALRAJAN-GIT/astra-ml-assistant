"""
Translation Service
Handles language detection and translation
"""
from typing import Dict, List, Optional
from deep_translator import GoogleTranslator
import re


class TranslationService:
    """Translation Service using Google Translate"""
    
    # Supported languages (30+ major languages)
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'nl': 'Dutch',
        'pl': 'Polish',
        'ru': 'Russian',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'bn': 'Bengali',
        'mr': 'Marathi',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ja': 'Japanese',
        'ko': 'Korean',
        'vi': 'Vietnamese',
        'th': 'Thai',
        'id': 'Indonesian',
        'tr': 'Turkish',
        'sv': 'Swedish',
        'da': 'Danish',
        'fi': 'Finnish',
        'no': 'Norwegian',
        'cs': 'Czech',
        'el': 'Greek',
        'he': 'Hebrew',
        'ro': 'Romanian',
        'uk': 'Ukrainian'
    }
    
    def __init__(self):
        """Initialize Translation Service"""
        pass
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text (simplified detection)
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code (e.g., 'en', 'es')
        """
        # Simple heuristic language detection
        # Check for non-Latin scripts
        if re.search(r'[\u0900-\u097F]', text):  # Devanagari (Hindi)
            return 'hi'
        elif re.search(r'[\u0B80-\u0BFF]', text):  # Tamil
            return 'ta'
        elif re.search(r'[\u0C00-\u0C7F]', text):  # Telugu
            return 'te'
        elif re.search(r'[\u0980-\u09FF]', text):  # Bengali
            return 'bn'
        elif re.search(r'[\u4E00-\u9FFF]', text):  # Chinese
            return 'zh-CN'
        elif re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):  # Japanese
            return 'ja'
        elif re.search(r'[\uAC00-\uD7AF]', text):  # Korean
            return 'ko'
        elif re.search(r'[\u0600-\u06FF]', text):  # Arabic
            return 'ar'
        elif re.search(r'[\u0400-\u04FF]', text):  # Cyrillic (Russian)
            return 'ru'
        else:
            # Default to English for Latin script
            return 'en'
    
    def translate(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """
        Translate text to target language while preserving markdown code blocks
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code ('auto' for auto-detect)
            
        Returns:
            Translated text
        """
        try:
            if target_lang not in self.SUPPORTED_LANGUAGES:
                return text  # Return original if language not supported
            
            # Don't translate if already in target language
            if source_lang == target_lang:
                return text
            
            return self.translate_markdown(text, target_lang, source_lang)
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original on error

    def translate_markdown(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """
        Translates markdown text while preserving code blocks and inline code.
        """
        # Regex to find code blocks (```...```) and inline code (`...`)
        code_pattern = r'(```[\s\S]*?```|`[^`\n]+`)'
        
        # Find all code segments
        placeholders = []
        
        def replace_code(match):
            placeholder = f"XYZCODEBLOCK{len(placeholders)}XYZ"
            placeholders.append(match.group(0))
            return placeholder

        # Temporarily replace code blocks with placeholders
        text_with_placeholders = re.sub(code_pattern, replace_code, text)
        
        # Translate the text parts
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_text = translator.translate(text_with_placeholders)
        
        # Restore code blocks
        for i, code in enumerate(placeholders):
            translated_text = translated_text.replace(f"XYZCODEBLOCK{i}XYZ", code)
            
        return translated_text
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages
        
        Returns:
            List of dictionaries with code and name
        """
        return [
            {'code': code, 'name': name}
            for code, name in self.SUPPORTED_LANGUAGES.items()
        ]
    
    def is_language_supported(self, lang_code: str) -> bool:
        """
        Check if language is supported
        
        Args:
            lang_code: Language code to check
            
        Returns:
            True if supported
        """
        return lang_code in self.SUPPORTED_LANGUAGES


# Singleton instance
translation_service = TranslationService()
