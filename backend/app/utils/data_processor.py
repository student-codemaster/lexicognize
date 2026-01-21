import json
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from langdetect import detect
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import nltk

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class LegalDataProcessor:
    """Processor for legal text datasets with analysis and validation capabilities"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.legal_terms = {
            'plaintiff', 'defendant', 'court', 'judge', 'jury', 'evidence', 'testimony',
            'witness', 'verdict', 'judgment', 'appeal', 'motion', 'complaint', 'lawsuit',
            'contract', 'agreement', 'liability', 'damages', 'breach', 'settlement',
            'statute', 'regulation', 'compliance', 'violation', 'penalty', 'fine'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\"\'\/]', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)
        
        # Remove multiple punctuation
        text = re.sub(r'[.,;:!?]{2,}', '.', text)
        
        # Strip and return
        return text.strip()
    
    def extract_legal_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract potential legal entities from text"""
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'legal_terms': []
        }
        
        # Simple regex patterns for entity extraction
        # Person names (simplified)
        person_pattern = r'\b([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        entities['persons'] = list(set(re.findall(person_pattern, text)))
        
        # Organizations (simplified)
        org_pattern = r'\b([A-Z][a-z]+(?:\s+(?:Inc|Corp|LLC|Ltd|Co|Company|Corporation|LLC|PLC)))\b'
        entities['organizations'] = list(set(re.findall(org_pattern, text)))
        
        # Dates
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
        entities['dates'] = list(set(re.findall(date_pattern, text)))
        
        # Legal terms
        words = word_tokenize(text.lower())
        entities['legal_terms'] = [word for word in words if word in self.legal_terms]
        
        return entities
    
    def detect_language(self, text: str) -> str:
        """Detect language of text"""
        try:
            return detect(text)
        except:
            return "unknown"
    
    def analyze_text_complexity(self, text: str) -> Dict[str, float]:
        """Analyze text complexity metrics"""
        if not text:
            return {'words_per_sentence': 0, 'avg_word_length': 0, 'readability_score': 0}
        
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Words per sentence
        words_per_sentence = len(words) / len(sentences) if sentences else 0
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Simple readability score (inverse of complexity)
        readability_score = 100 / (1 + words_per_sentence * 0.1 + avg_word_length * 2)
        
        return {
            'words_per_sentence': round(words_per_sentence, 2),
            'avg_word_length': round(avg_word_length, 2),
            'readability_score': round(readability_score, 2)
        }
    
    def validate_sample(self, sample: Dict) -> Tuple[bool, List[str]]:
        """Validate a single data sample"""
        errors = []
        
        # Check required fields
        if 'text' not in sample or not sample['text']:
            errors.append("Missing or empty 'text' field")
        
        if 'summary' not in sample or not sample['summary']:
            errors.append("Missing or empty 'summary' field")
        
        # Check text length
        if 'text' in sample:
            text_len = len(sample['text'])
            if text_len < 50:
                errors.append("Text too short (< 50 characters)")
            elif text_len > 50000:
                errors.append("Text too long (> 50000 characters)")
        
        # Check summary length
        if 'summary' in sample:
            summary_len = len(sample['summary'])
            if summary_len < 10:
                errors.append("Summary too short (< 10 characters)")
            elif summary_len > 5000:
                errors.append("Summary too long (> 5000 characters)")
        
        # Check for content overlap (simplified)
        if 'text' in sample and 'summary' in sample:
            text_words = set(word_tokenize(sample['text'].lower()))
            summary_words = set(word_tokenize(sample['summary'].lower()))
            
            if text_words and summary_words:
                overlap = len(text_words.intersection(summary_words)) / len(summary_words)
                if overlap > 0.9:
                    errors.append("Summary too similar to original text")
        
        return len(errors) == 0, errors
    
    def process_dataset(self, data: List[Dict]) -> List[Dict]:
        """Process and clean a dataset"""
        processed_data = []
        
        for i, sample in enumerate(data):
            try:
                # Clean text fields
                if 'text' in sample:
                    sample['text'] = self.clean_text(sample['text'])
                
                if 'summary' in sample:
                    sample['summary'] = self.clean_text(sample['summary'])
                
                if 'simplified' in sample:
                    sample['simplified'] = self.clean_text(sample['simplified'])
                
                # Add metadata
                sample['processed_at'] = datetime.now().isoformat()
                sample['text_length'] = len(sample.get('text', ''))
                sample['summary_length'] = len(sample.get('summary', ''))
                
                # Detect language
                if 'text' in sample:
                    sample['language'] = self.detect_language(sample['text'])
                
                # Analyze complexity
                if 'text' in sample:
                    sample['complexity'] = self.analyze_text_complexity(sample['text'])
                
                # Extract entities
                if 'text' in sample:
                    sample['entities'] = self.extract_legal_entities(sample['text'])
                
                # Validate
                is_valid, errors = self.validate_sample(sample)
                sample['is_valid'] = is_valid
                sample['validation_errors'] = errors
                
                processed_data.append(sample)
                
            except Exception as e:
                logger.warning(f"Error processing sample {i}: {e}")
                continue
        
        return processed_data
    
    def calculate_statistics(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate comprehensive dataset statistics"""
        if not data:
            return {"error": "Empty dataset"}
        
        stats = {
            'total_samples': len(data),
            'valid_samples': sum(1 for sample in data if sample.get('is_valid', True)),
            'invalid_samples': sum(1 for sample in data if not sample.get('is_valid', True)),
            'languages': {},
            'categories': {},
            'text_lengths': [],
            'summary_lengths': [],
            'complexity_scores': [],
            'legal_terms_frequency': {},
            'sources_distribution': {}
        }
        
        for sample in data:
            # Language distribution
            lang = sample.get('language', 'unknown')
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
            
            # Category distribution
            category = sample.get('category', 'general')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            # Length statistics
            if 'text_length' in sample:
                stats['text_lengths'].append(sample['text_length'])
            
            if 'summary_length' in sample:
                stats['summary_lengths'].append(sample['summary_length'])
            
            # Complexity scores
            if 'complexity' in sample and 'readability_score' in sample['complexity']:
                stats['complexity_scores'].append(sample['complexity']['readability_score'])
            
            # Legal terms frequency
            if 'entities' in sample and 'legal_terms' in sample['entities']:
                for term in sample['entities']['legal_terms']:
                    stats['legal_terms_frequency'][term] = stats['legal_terms_frequency'].get(term, 0) + 1
            
            # Sources distribution (for multi_lexsum)
            if 'sources_count' in sample:
                count = sample['sources_count']
                stats['sources_distribution'][str(count)] = stats['sources_distribution'].get(str(count), 0) + 1
        
        # Calculate summary statistics
        if stats['text_lengths']:
            stats['text_length_stats'] = {
                'mean': np.mean(stats['text_lengths']),
                'median': np.median(stats['text_lengths']),
                'min': min(stats['text_lengths']),
                'max': max(stats['text_lengths']),
                'std': np.std(stats['text_lengths'])
            }
        
        if stats['summary_lengths']:
            stats['summary_length_stats'] = {
                'mean': np.mean(stats['summary_lengths']),
                'median': np.median(stats['summary_lengths']),
                'min': min(stats['summary_lengths']),
                'max': max(stats['summary_lengths']),
                'std': np.std(stats['summary_lengths'])
            }
        
        if stats['complexity_scores']:
            stats['complexity_stats'] = {
                'mean': np.mean(stats['complexity_scores']),
                'median': np.median(stats['complexity_scores']),
                'min': min(stats['complexity_scores']),
                'max': max(stats['complexity_scores'])
            }
        
        # Top legal terms
        if stats['legal_terms_frequency']:
            stats['top_legal_terms'] = dict(
                Counter(stats['legal_terms_frequency']).most_common(10)
            )
        
        # Validation rate
        stats['validation_rate'] = stats['valid_samples'] / stats['total_samples'] * 100
        
        return stats
    
    def filter_dataset(
        self,
        data: List[Dict],
        min_text_length: int = 100,
        max_text_length: int = 10000,
        min_summary_length: int = 10,
        max_summary_length: int = 1000,
        languages: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        only_valid: bool = True
    ) -> List[Dict]:
        """Filter dataset based on various criteria"""
        filtered_data = []
        
        for sample in data:
            # Skip invalid samples if requested
            if only_valid and not sample.get('is_valid', True):
                continue
            
            # Length filters
            text_len = sample.get('text_length', len(sample.get('text', '')))
            summary_len = sample.get('summary_length', len(sample.get('summary', '')))
            
            if text_len < min_text_length or text_len > max_text_length:
                continue
            
            if summary_len < min_summary_length or summary_len > max_summary_length:
                continue
            
            # Language filter
            if languages and sample.get('language') not in languages:
                continue
            
            # Category filter
            if categories and sample.get('category') not in categories:
                continue
            
            filtered_data.append(sample)
        
        return filtered_data
    
    def export_dataset(
        self,
        data: List[Dict],
        output_path: str,
        format: str = 'json'
    ) -> bool:
        """Export dataset to various formats"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            elif format.lower() == 'csv':
                # Flatten nested dictionaries for CSV
                flattened_data = []
                for sample in data:
                    flat_sample = {}
                    for key, value in sample.items():
                        if isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                flat_sample[f"{key}_{sub_key}"] = sub_value
                        else:
                            flat_sample[key] = value
                    flattened_data.append(flat_sample)
                
                df = pd.DataFrame(flattened_data)
                df.to_csv(output_path, index=False)
            
            logger.info(f"Dataset exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting dataset: {e}")
            return False