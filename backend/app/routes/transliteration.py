from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from app.utils.transliterator import LegalTransliterator
from app.utils.language_utils import LanguageUtils

router = APIRouter()
transliterator = LegalTransliterator()

class TransliterationRequest(BaseModel):
    text: str
    source_language: str
    target_language: str
    preserve_terms: bool = True

class BatchTransliterationRequest(BaseModel):
    texts: List[str]
    source_language: str
    target_language: str
    preserve_terms: bool = True

@router.post("/transliterate")
async def transliterate_text(request: TransliterationRequest):
    """Transliterate text between scripts"""
    try:
        result = transliterator.transliterate_with_preservation(
            request.text,
            request.source_language,
            request.target_language,
            request.preserve_terms
        )
        
        # Add language names
        result['source_language_name'] = LanguageUtils.get_language_name(request.source_language)
        result['target_language_name'] = LanguageUtils.get_language_name(request.target_language)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transliteration error: {str(e)}")

@router.post("/transliterate-batch")
async def transliterate_batch(request: BatchTransliterationRequest):
    """Transliterate batch of texts"""
    try:
        results = transliterator.batch_transliterate(
            request.texts,
            request.source_language,
            request.target_language
        )
        
        return {
            'results': results,
            'count': len(results),
            'source_language': request.source_language,
            'target_language': request.target_language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch transliteration error: {str(e)}")

@router.post("/detect-script")
async def detect_script(text: str):
    """Detect script of the text"""
    try:
        script = transliterator.detect_script(text)
        
        # Try to infer language from script
        script_to_lang = {
            'devanagari': ['hi', 'mr', 'sa'],
            'tamil': ['ta'],
            'kannada': ['kn'],
            'telugu': ['te'],
            'malayalam': ['ml'],
            'bengali': ['bn'],
            'gujarati': ['gu'],
            'gurmukhi': ['pa'],
            'oriya': ['or']
        }
        
        possible_languages = []
        for script_name, langs in script_to_lang.items():
            if script_name in script.lower():
                possible_languages.extend(langs)
        
        return {
            'text': text,
            'detected_script': script,
            'possible_languages': possible_languages,
            'language_names': [LanguageUtils.get_language_name(lang) for lang in possible_languages]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script detection error: {str(e)}")

@router.get("/supported-scripts")
async def get_supported_scripts():
    """Get list of supported scripts for transliteration"""
    try:
        scripts = []
        for lang_code, script in transliterator.SCRIPTS.items():
            scripts.append({
                'language_code': lang_code,
                'language_name': LanguageUtils.get_language_name(lang_code),
                'script': script,
                'script_name': script.upper()
            })
        
        return {
            'scripts': scripts,
            'total_scripts': len(scripts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scripts: {str(e)}")

@router.post("/legal-terms-transliterate")
async def transliterate_legal_terms(request: TransliterationRequest):
    """Transliterate with special handling for legal terms"""
    try:
        transliterated = transliterator.transliterate_legal_terms(
            request.text,
            request.source_language,
            request.target_language
        )
        
        return {
            'original_text': request.text,
            'transliterated_text': transliterated,
            'source_language': request.source_language,
            'target_language': request.target_language,
            'source_language_name': LanguageUtils.get_language_name(request.source_language),
            'target_language_name': LanguageUtils.get_language_name(request.target_language)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Legal terms transliteration error: {str(e)}")