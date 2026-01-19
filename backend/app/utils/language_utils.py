import re
from typing import Dict, List, Optional, Tuple
import langid
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0

class LanguageUtils:
    """Utility class for language detection and processing"""
    
    # Language code mapping
    LANGUAGES = {
        'en': 'English',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'kn': 'Kannada',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'or': 'Odia',
        'ur': 'Urdu'
    }
    
    # Language script mapping
    SCRIPTS = {
        'hi': 'Devanagari',
        'ta': 'Tamil',
        'kn': 'Kannada',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'pa': 'Gurmukhi',
        'or': 'Odia',
        'ur': 'Arabic'
    }
    
    @staticmethod
    def detect_language(text: str) -> Tuple[str, float]:
        """Detect language with confidence score"""
        try:
            # Use langid for detection with confidence
            lang, confidence = langid.classify(text)
            return lang, confidence
        except:
            try:
                # Fallback to langdetect
                lang = detect(text)
                return lang, 0.8  # Default confidence
            except:
                return 'en', 0.5  # Default to English
    
    @staticmethod
    def is_indian_language(lang_code: str) -> bool:
        """Check if language is Indian"""
        indian_langs = {'hi', 'ta', 'kn', 'te', 'ml', 'bn', 'mr', 'gu', 'pa', 'or', 'ur'}
        return lang_code in indian_langs
    
    @staticmethod
    def get_language_name(lang_code: str) -> str:
        """Get full language name from code"""
        return LanguageUtils.LANGUAGES.get(lang_code, 'Unknown')
    
    @staticmethod
    def get_script(lang_code: str) -> str:
        """Get script for language"""
        return LanguageUtils.SCRIPTS.get(lang_code, 'Latin')
    
    @staticmethod
    def split_text_by_language(text: str) -> List[Dict]:
        """Split multilingual text by language segments"""
        # Simple heuristic: split by sentences and detect language for each
        sentences = re.split(r'[.!?।॥]+', text)
        segments = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                lang, confidence = LanguageUtils.detect_language(sentence)
                if confidence > 0.7:  # Only add if confident
                    segments.append({
                        'text': sentence,
                        'language': lang,
                        'confidence': confidence,
                        'language_name': LanguageUtils.get_language_name(lang)
                    })
        
        return segments
    
    @staticmethod
    def validate_text_for_language(text: str, lang_code: str) -> bool:
        """Validate if text matches expected language"""
        detected_lang, confidence = LanguageUtils.detect_language(text)
        return detected_lang == lang_code and confidence > 0.7