import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline,
    MarianMTModel,
    MarianTokenizer
)
from typing import List, Dict, Optional, Union
import logging
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.utils.language_utils import LanguageUtils

logger = logging.getLogger(__name__)

class LegalTranslator:
    """Translation service for legal text with support for Indian languages"""
    
    # Model mapping for different language pairs
    TRANSLATION_MODELS = {
        # English to Indian languages
        'en-hi': 'Helsinki-NLP/opus-mt-en-hi',
        'en-ta': 'Helsinki-NLP/opus-mt-en-ta',
        'en-kn': 'Helsinki-NLP/opus-mt-en-kn',
        'en-te': 'Helsinki-NLP/opus-mt-en-te',
        'en-ml': 'Helsinki-NLP/opus-mt-en-ml',
        'en-bn': 'Helsinki-NLP/opus-mt-en-bn',
        'en-mr': 'Helsinki-NLP/opus-mt-en-mr',
        'en-gu': 'Helsinki-NLP/opus-mt-en-gu',
        
        # Indian languages to English
        'hi-en': 'Helsinki-NLP/opus-mt-hi-en',
        'ta-en': 'Helsinki-NLP/opus-mt-ta-en',
        'kn-en': 'Helsinki-NLP/opus-mt-kn-en',
        'te-en': 'Helsinki-NLP/opus-mt-te-en',
        'ml-en': 'Helsinki-NLP/opus-mt-ml-en',
        'bn-en': 'Helsinki-NLP/opus-mt-bn-en',
        'mr-en': 'Helsinki-NLP/opus-mt-mr-en',
        'gu-en': 'Helsinki-NLP/opus-mt-gu-en',
        
        # Between Indian languages (via English pivot)
        'hi-ta': 'pivot',
        'hi-kn': 'pivot',
        'ta-hi': 'pivot',
        'ta-kn': 'pivot',
        'kn-hi': 'pivot',
        'kn-ta': 'pivot',
    }
    
    def __init__(self, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.tokenizers = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        logger.info(f"Translator initialized on device: {self.device}")
    
    @lru_cache(maxsize=10)
    def load_model(self, model_name: str):
        """Load translation model with caching"""
        try:
            logger.info(f"Loading translation model: {model_name}")
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            model = model.to(self.device)
            model.eval()
            
            return model, tokenizer
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise
    
    def get_model_key(self, src_lang: str, tgt_lang: str) -> str:
        """Get model key for language pair"""
        return f"{src_lang}-{tgt_lang}"
    
    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        max_length: int = 512,
        batch_size: int = 8
    ) -> str:
        """Translate text from source to target language"""
        
        if source_lang == target_lang:
            return text
        
        model_key = self.get_model_key(source_lang, target_lang)
        
        if model_key not in self.TRANSLATION_MODELS:
            raise ValueError(f"Translation not supported for {model_key}")
        
        model_name = self.TRANSLATION_MODELS[model_key]
        
        if model_name == 'pivot':
            # Use English as pivot language
            english_text = self.translate_text(text, source_lang, 'en', max_length)
            return self.translate_text(english_text, 'en', target_lang, max_length)
        
        try:
            model, tokenizer = self.load_model(model_name)
            
            # Prepare text
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=max_length)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                translated = model.generate(
                    **inputs,
                    max_length=max_length,
                    num_beams=4,
                    temperature=0.7,
                    do_sample=True
                )
            
            # Decode
            translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            
            return translated_text
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise
    
    async def translate_batch(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str,
        max_length: int = 512
    ) -> List[str]:
        """Translate batch of texts asynchronously"""
        loop = asyncio.get_event_loop()
        
        def translate_batch_sync():
            translated_texts = []
            for text in texts:
                translated = self.translate_text(text, source_lang, target_lang, max_length)
                translated_texts.append(translated)
            return translated_texts
        
        return await loop.run_in_executor(self.executor, translate_batch_sync)
    
    def translate_legal_document(
        self,
        document: Dict,
        target_lang: str,
        fields: List[str] = None
    ) -> Dict:
        """Translate legal document to target language"""
        if fields is None:
            fields = ['text', 'summary', 'simplified', 'title', 'description']
        
        translated_doc = document.copy()
        source_lang = 'en'  # Assuming English source
        
        for field in fields:
            if field in document and document[field]:
                try:
                    translated_text = self.translate_text(
                        document[field],
                        source_lang,
                        target_lang,
                        max_length=1024
                    )
                    translated_doc[f"{field}_{target_lang}"] = translated_text
                except Exception as e:
                    logger.error(f"Error translating field {field}: {e}")
                    translated_doc[f"{field}_{target_lang}"] = f"[Translation failed: {str(e)}]"
        
        translated_doc['translated_to'] = target_lang
        translated_doc['original_language'] = source_lang
        
        return translated_doc
    
    def detect_and_translate(
        self,
        text: str,
        target_lang: str,
        fallback_lang: str = 'en'
    ) -> Dict:
        """Detect language and translate to target"""
        detected_lang, confidence = LanguageUtils.detect_language(text)
        
        result = {
            'original_text': text,
            'detected_language': detected_lang,
            'detected_language_name': LanguageUtils.get_language_name(detected_lang),
            'confidence': confidence,
            'target_language': target_lang,
            'target_language_name': LanguageUtils.get_language_name(target_lang)
        }
        
        if detected_lang == target_lang:
            result['translated_text'] = text
            result['translation_needed'] = False
        else:
            try:
                translated = self.translate_text(text, detected_lang, target_lang)
                result['translated_text'] = translated
                result['translation_needed'] = True
            except Exception as e:
                # Try fallback language
                if fallback_lang and detected_lang != fallback_lang:
                    try:
                        # Translate to fallback first, then to target
                        fallback_text = self.translate_text(text, detected_lang, fallback_lang)
                        translated = self.translate_text(fallback_text, fallback_lang, target_lang)
                        result['translated_text'] = translated
                        result['translation_needed'] = True
                        result['used_fallback'] = True
                        result['fallback_language'] = fallback_lang
                    except Exception as e2:
                        result['error'] = str(e2)
                        result['translated_text'] = text
                else:
                    result['error'] = str(e)
                    result['translated_text'] = text
        
        return result
    
    def get_supported_languages(self) -> Dict:
        """Get list of supported languages and pairs"""
        supported = {
            'source_languages': set(),
            'target_languages': set(),
            'language_pairs': list(self.TRANSLATION_MODELS.keys())
        }
        
        for pair in self.TRANSLATION_MODELS.keys():
            src, tgt = pair.split('-')
            supported['source_languages'].add(src)
            supported['target_languages'].add(tgt)
        
        # Convert sets to lists
        supported['source_languages'] = list(supported['source_languages'])
        supported['target_languages'] = list(supported['target_languages'])
        
        # Add language names
        supported['language_names'] = {
            code: LanguageUtils.get_language_name(code)
            for code in set(supported['source_languages']).union(supported['target_languages'])
        }
        
        return supported