import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import indic_transliteration
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import regex as re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LegalTransliterator:
    """Transliteration service for Indian languages"""
    
    # Script mapping for transliteration
    SCRIPTS = {
        'hi': sanscript.DEVANAGARI,
        'ta': sanscript.TAMIL,
        'kn': sanscript.KANNADA,
        'te': sanscript.TELUGU,
        'ml': sanscript.MALAYALAM,
        'bn': sanscript.BENGALI,
        'gu': sanscript.GUJARATI,
        'pa': sanscript.GURMUKHI,
        'or': sanscript.ORIYA,
        'ur': sanscript.ARABIC,
        'en': sanscript.ITRANS
    }
    
    # Model for transliteration
    TRANSLITERATION_MODELS = {
        'hi': 'ai4bharat/IndicTrans',
        'ta': 'ai4bharat/IndicTrans',
        'kn': 'ai4bharat/IndicTrans',
        'te': 'ai4bharat/IndicTrans',
        'ml': 'ai4bharat/IndicTrans',
        'bn': 'ai4bharat/IndicTrans',
        'gu': 'ai4bharat/IndicTrans',
        'pa': 'ai4bharat/IndicTrans',
        'or': 'ai4bharat/IndicTrans',
        'ur': 'ai4bharat/IndicTrans'
    }
    
    def __init__(self, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        logger.info(f"Transliterator initialized on device: {self.device}")
    
    def transliterate_text(
        self,
        text: str,
        source_script: str,
        target_script: str
    ) -> str:
        """Transliterate text between scripts using indic-transliteration"""
        try:
            if source_script == target_script:
                return text
            
            # Use indic-transliteration library
            transliterated = transliterate(
                text,
                source_script,
                target_script
            )
            
            return transliterated
            
        except Exception as e:
            logger.error(f"Transliteration error: {e}")
            # Fallback to regex-based transliteration for common cases
            return self._fallback_transliterate(text, source_script, target_script)
    
    def _fallback_transliterate(self, text: str, source_script: str, target_script: str) -> str:
        """Fallback transliteration for common patterns"""
        # Simple vowel mapping for Indian languages
        vowel_mapping = {
            sanscript.DEVANAGARI: {'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo'},
            sanscript.TAMIL: {'அ': 'a', 'ஆ': 'aa', 'இ': 'i', 'ஈ': 'ee', 'உ': 'u', 'ஊ': 'oo'},
            sanscript.KANNADA: {'ಅ': 'a', 'ಆ': 'aa', 'ಇ': 'i', 'ಈ': 'ee', 'ಉ': 'u', 'ಊ': 'oo'},
        }
        
        if source_script in vowel_mapping and target_script == sanscript.ITRANS:
            # Convert to ITRANS (English-like)
            mapping = vowel_mapping[source_script]
            for src, tgt in mapping.items():
                text = text.replace(src, tgt)
        
        return text
    
    def transliterate_legal_terms(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Transliterate legal terms with special handling"""
        
        # Common legal terms in Indian languages
        legal_terms = {
            'hi': {
                'न्यायालय': 'court',
                'कानून': 'law',
                'अधिवक्ता': 'advocate',
                'निर्णय': 'judgment',
                'अपील': 'appeal'
            },
            'ta': {
                'நீதிமன்றம்': 'court',
                'சட்டம்': 'law',
                'வழக்கறிஞர்': 'advocate',
                'தீர்ப்பு': 'judgment',
                'மேல்முறையீடு': 'appeal'
            },
            'kn': {
                'ನ್ಯಾಯಾಲಯ': 'court',
                'ಕಾನೂನು': 'law',
                'ವಕೀಲ': 'advocate',
                'ತೀರ್ಪು': 'judgment',
                'ಮೇಲ್ಮನವಿ': 'appeal'
            }
        }
        
        # Replace legal terms with translations first
        if source_lang in legal_terms:
            for term, translation in legal_terms[source_lang].items():
                text = text.replace(term, f"{term} ({translation})")
        
        # Then transliterate
        source_script = self.SCRIPTS.get(source_lang, sanscript.ITRANS)
        target_script = self.SCRIPTS.get(target_lang, sanscript.ITRANS)
        
        return self.transliterate_text(text, source_script, target_script)
    
    def detect_script(self, text: str) -> str:
        """Detect script of the text"""
        # Check for Devanagari (Hindi, Marathi, Sanskrit)
        if re.search(r'[\u0900-\u097F]', text):
            return sanscript.DEVANAGARI
        
        # Check for Tamil
        if re.search(r'[\u0B80-\u0BFF]', text):
            return sanscript.TAMIL
        
        # Check for Kannada
        if re.search(r'[\u0C80-\u0CFF]', text):
            return sanscript.KANNADA
        
        # Check for Telugu
        if re.search(r'[\u0C00-\u0C7F]', text):
            return sanscript.TELUGU
        
        # Check for Malayalam
        if re.search(r'[\u0D00-\u0D7F]', text):
            return sanscript.MALAYALAM
        
        # Check for Bengali
        if re.search(r'[\u0980-\u09FF]', text):
            return sanscript.BENGALI
        
        # Default to Latin/ITRANS
        return sanscript.ITRANS
    
    def transliterate_with_preservation(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        preserve_terms: bool = True
    ) -> Dict:
        """Transliterate with preservation of special terms and formatting"""
        
        result = {
            'original_text': text,
            'source_language': source_lang,
            'target_language': target_lang,
            'source_script': self.SCRIPTS.get(source_lang, sanscript.ITRANS),
            'target_script': self.SCRIPTS.get(target_lang, sanscript.ITRANS)
        }
        
        if preserve_terms:
            # Preserve legal citations and numbers
            preserved_sections = []
            
            # Find and preserve legal citations like [2023] SC 123
            citations = re.findall(r'\[\d{4}\].*?\d+', text)
            for citation in citations:
                placeholder = f"__CITATION_{len(preserved_sections)}__"
                text = text.replace(citation, placeholder)
                preserved_sections.append(('citation', citation))
            
            # Find and preserve section numbers like Section 123, Art. 45
            sections = re.findall(r'(?:Section|Art\.|Article|Rule|Regulation)\s+\d+[A-Za-z]*', text, re.IGNORECASE)
            for section in sections:
                placeholder = f"__SECTION_{len(preserved_sections)}__"
                text = text.replace(section, placeholder)
                preserved_sections.append(('section', section))
            
            # Find and preserve dates
            dates = re.findall(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text)
            for date in dates:
                placeholder = f"__DATE_{len(preserved_sections)}__"
                text = text.replace(date, placeholder)
                preserved_sections.append(('date', date))
        
        # Perform transliteration
        transliterated = self.transliterate_legal_terms(text, source_lang, target_lang)
        
        # Restore preserved sections
        if preserve_terms:
            for i, (type_, original) in enumerate(preserved_sections):
                placeholder = f"__{type_.upper()}_{i}__"
                transliterated = transliterated.replace(placeholder, original)
        
        result['transliterated_text'] = transliterated
        result['preserved_sections'] = preserved_sections if preserve_terms else []
        
        return result
    
    def batch_transliterate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[Dict]:
        """Transliterate batch of texts"""
        results = []
        for text in texts:
            result = self.transliterate_with_preservation(
                text, source_lang, target_lang
            )
            results.append(result)
        return results