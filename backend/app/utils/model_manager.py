import os
import json
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline,
    Trainer,
    TrainingArguments
)
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelManager:
    """Manager for loading and using trained models"""
    
    _models_cache = {}
    _tokenizers_cache = {}
    
    @staticmethod
    def get_available_models() -> List[Dict[str, Any]]:
        """Get list of all available trained models"""
        models_dir = "data/models"
        available_models = []
        
        if os.path.exists(models_dir):
            for model_name in os.listdir(models_dir):
                model_path = os.path.join(models_dir, model_name)
                if os.path.isdir(model_path):
                    # Check if it's a valid model directory
                    config_path = os.path.join(model_path, "config.json")
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, 'r') as f:
                                config = json.load(f)
                            
                            # Load metadata if exists
                            metadata_path = os.path.join(model_path, "metadata.json")
                            metadata = {}
                            if os.path.exists(metadata_path):
                                with open(metadata_path, 'r') as f:
                                    metadata = json.load(f)
                            
                            available_models.append({
                                "name": model_name,
                                "path": model_path,
                                "config": config,
                                "metadata": metadata,
                                "type": metadata.get("model_type", "unknown"),
                                "task": metadata.get("task", "unknown"),
                                "created_at": metadata.get("created_at", 
                                                         datetime.fromtimestamp(os.path.getmtime(model_path)).isoformat())
                            })
                        except Exception as e:
                            logger.error(f"Error loading model info for {model_name}: {e}")
        
        return available_models
    
    @staticmethod
    def load_model(model_name: str, use_cache: bool = True):
        """Load a trained model"""
        if use_cache and model_name in ModelManager._models_cache:
            return ModelManager._models_cache[model_name]
        
        models_dir = "data/models"
        model_path = os.path.join(models_dir, model_name)
        
        if not os.path.exists(model_path):
            raise ValueError(f"Model {model_name} not found")
        
        try:
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            # Load model
            model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            
            # Move to GPU if available
            device = 0 if torch.cuda.is_available() else -1
            if device >= 0:
                model = model.to(device)
            
            if use_cache:
                ModelManager._models_cache[model_name] = model
                ModelManager._tokenizers_cache[model_name] = tokenizer
            
            return model, tokenizer, device
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            raise
    
    @staticmethod
    async def generate_summary(
        model_name: str,
        text: str,
        max_length: int = 512,
        min_length: int = 50,
        num_beams: int = 4,
        temperature: float = 1.0
    ) -> str:
        """Generate summary using specified model"""
        try:
            model, tokenizer, device = ModelManager.load_model(model_name)
            
            # Create summarization pipeline
            summarizer = pipeline(
                "summarization",
                model=model,
                tokenizer=tokenizer,
                device=device
            )
            
            # Split long text into chunks if needed
            if len(text.split()) > 1000:
                chunks = ModelManager._chunk_text(text, max_chunk_size=1000)
                summaries = []
                
                for chunk in chunks:
                    summary = summarizer(
                        chunk,
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=num_beams,
                        temperature=temperature,
                        do_sample=True
                    )[0]['summary_text']
                    summaries.append(summary)
                
                # Combine chunk summaries
                combined_summary = " ".join(summaries)
                # Summarize the combined summary if it's too long
                if len(combined_summary.split()) > 500:
                    final_summary = summarizer(
                        combined_summary,
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=num_beams,
                        temperature=temperature,
                        do_sample=True
                    )[0]['summary_text']
                else:
                    final_summary = combined_summary
            else:
                final_summary = summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=num_beams,
                    temperature=temperature,
                    do_sample=True
                )[0]['summary_text']
            
            return final_summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    @staticmethod
    async def generate_simplification(
        model_name: str,
        text: str,
        max_length: int = 512,
        min_length: int = 50,
        num_beams: int = 4,
        temperature: float = 1.0
    ) -> str:
        """Generate simplified text using specified model"""
        try:
            model, tokenizer, device = ModelManager.load_model(model_name)
            
            # Create text2text generation pipeline
            simplifier = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                device=device
            )
            
            # Create prompt for simplification
            prompt = f"Simplify the following legal text: {text}"
            
            simplified = simplifier(
                prompt,
                max_length=max_length,
                min_length=min_length,
                num_beams=num_beams,
                temperature=temperature,
                do_sample=True
            )[0]['generated_text']
            
            return simplified
            
        except Exception as e:
            logger.error(f"Error generating simplification: {e}")
            raise
    
    @staticmethod
    def _chunk_text(text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split text into chunks of specified word size"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), max_chunk_size):
            chunk = " ".join(words[i:i + max_chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def save_model_metadata(model_path: str, metadata: Dict[str, Any]):
        """Save metadata for a trained model"""
        metadata_path = os.path.join(model_path, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    @staticmethod
    def get_model_metadata(model_name: str) -> Dict[str, Any]:
        """Get metadata for a trained model"""
        models_dir = "data/models"
        model_path = os.path.join(models_dir, model_name)
        metadata_path = os.path.join(model_path, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        
        return {}