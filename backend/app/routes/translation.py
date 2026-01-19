from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio

from app.utils.translator import LegalTranslator
from app.utils.language_utils import LanguageUtils

router = APIRouter()
translator = LegalTranslator()

class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = None
    target_language: str
    detect_language: bool = True
    preserve_formatting: bool = True
    max_length: int = 1024

class BatchTranslationRequest(BaseModel):
    texts: List[str]
    source_language: Optional[str] = None
    target_language: str
    detect_language: bool = True

class DocumentTranslationRequest(BaseModel):
    document: Dict
    target_language: str
    fields: List[str] = None

@router.post("/translate")
async def translate_text(request: TranslationRequest):
    """Translate text to target language"""
    try:
        if request.detect_language and not request.source_language:
            # Auto-detect language
            result = translator.detect_and_translate(
                request.text,
                request.target_language
            )
        else:
            # Use specified source language
            source_lang = request.source_language or 'en'
            translated_text = translator.translate_text(
                request.text,
                source_lang,
                request.target_language,
                max_length=request.max_length
            )
            
            result = {
                'original_text': request.text,
                'translated_text': translated_text,
                'source_language': source_lang,
                'target_language': request.target_language,
                'source_language_name': LanguageUtils.get_language_name(source_lang),
                'target_language_name': LanguageUtils.get_language_name(request.target_language),
                'translation_needed': source_lang != request.target_language
            }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@router.post("/translate-batch")
async def translate_batch(request: BatchTranslationRequest):
    """Translate batch of texts"""
    try:
        if request.detect_language:
            # Detect language for each text and translate
            results = []
            for text in request.texts:
                lang, confidence = LanguageUtils.detect_language(text)
                source_lang = lang if confidence > 0.7 else 'en'
                
                translated = translator.translate_text(
                    text,
                    source_lang,
                    request.target_language
                )
                
                results.append({
                    'original_text': text,
                    'translated_text': translated,
                    'detected_language': source_lang,
                    'confidence': confidence
                })
        else:
            source_lang = request.source_language or 'en'
            translated_texts = await translator.translate_batch(
                request.texts,
                source_lang,
                request.target_language
            )
            
            results = [
                {
                    'original_text': text,
                    'translated_text': translated,
                    'source_language': source_lang
                }
                for text, translated in zip(request.texts, translated_texts)
            ]
        
        return {
            'results': results,
            'count': len(results),
            'target_language': request.target_language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch translation error: {str(e)}")

@router.post("/translate-document")
async def translate_document(request: DocumentTranslationRequest):
    """Translate legal document"""
    try:
        translated_doc = translator.translate_legal_document(
            request.document,
            request.target_language,
            request.fields
        )
        
        return {
            'original_document': request.document,
            'translated_document': translated_doc,
            'target_language': request.target_language,
            'translated_fields': [f for f in request.fields or [] if f in request.document]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document translation error: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    try:
        supported = translator.get_supported_languages()
        
        # Add language details
        languages = []
        for lang_code in supported['source_languages']:
            languages.append({
                'code': lang_code,
                'name': LanguageUtils.get_language_name(lang_code),
                'script': LanguageUtils.get_script(lang_code),
                'is_indian': LanguageUtils.is_indian_language(lang_code)
            })
        
        return {
            'languages': languages,
            'language_pairs': supported['language_pairs'],
            'total_languages': len(languages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting languages: {str(e)}")

@router.post("/detect-language")
async def detect_language(text: str):
    """Detect language of text"""
    try:
        lang_code, confidence = LanguageUtils.detect_language(text)
        
        return {
            'text': text,
            'detected_language': lang_code,
            'language_name': LanguageUtils.get_language_name(lang_code),
            'confidence': confidence,
            'script': LanguageUtils.get_script(lang_code),
            'is_indian': LanguageUtils.is_indian_language(lang_code)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection error: {str(e)}")

@router.post("/split-by-language")
async def split_by_language(text: str):
    """Split multilingual text by language segments"""
    try:
        segments = LanguageUtils.split_text_by_language(text)
        
        return {
            'original_text': text,
            'segments': segments,
            'total_segments': len(segments),
            'languages_found': list(set(seg['language'] for seg in segments))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error splitting text: {str(e)}")