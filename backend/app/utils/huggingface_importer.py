import json
import os
from typing import Dict, List, Optional, Any
import logging
from datasets import load_dataset, Dataset, DatasetDict
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class HuggingFaceDatasetImporter:
    """Import datasets from Hugging Face Hub"""
    
    SUPPORTED_DATASETS = {
        "wikilarge": {
            "path": "waboucay/wikilarge",
            "description": "Wikipedia simplification dataset with original and simplified sentences",
            "task": "simplification",
            "languages": ["en"],
            "fields": ["original", "simplification"]
        },
        "legal_bench": {
            "path": "nguha/legalbench",
            "description": "Legal NLP benchmark dataset",
            "task": "legal_classification",
            "languages": ["en"],
            "fields": ["text", "label"]
        },
        "contract_nli": {
            "path": "MaestroGecko/contract-nli",
            "description": "Contract Natural Language Inference dataset",
            "task": "nli",
            "languages": ["en"],
            "fields": ["premise", "hypothesis", "label"]
        },
        "eurlex": {
            "path": "multi_eurlex",
            "description": "Multi-lingual EU legislation dataset",
            "task": "classification",
            "languages": ["en", "de", "fr", "es", "it", "pl"],
            "fields": ["text", "labels"]
        },
        "caselaw": {
            "path": "lex_glue",
            "description": "Legal case law dataset",
            "task": "summarization",
            "languages": ["en"],
            "fields": ["text", "summary"]
        },
        "xsum": {
            "path": "EdinburghNLP/xsum",
            "description": "Extreme Summarization dataset",
            "task": "summarization",
            "languages": ["en"],
            "fields": ["document", "summary"]
        },
        "cnn_dailymail": {
            "path": "cnn_dailymail",
            "description": "News article summarization dataset",
            "task": "summarization",
            "languages": ["en"],
            "fields": ["article", "highlights"]
        },
        "samsum": {
            "path": "samsum",
            "description": "Conversation summarization dataset",
            "task": "summarization",
            "languages": ["en"],
            "fields": ["dialogue", "summary"]
        },
        "multi_lexsum": {
            "path": "allenai/multi_lexsum",
            "description": "Multi-lingual legal summarization dataset with long, short, and tiny summaries",
            "task": "summarization",
            "languages": ["en"],
            "fields": ["sources", "summary/long", "summary/short", "summary/tiny"],
            "name": "v20220616"
        }
    }
    
    @staticmethod
    def get_available_datasets() -> List[Dict[str, Any]]:
        """Get list of available datasets from Hugging Face"""
        datasets = []
        
        for key, config in HuggingFaceDatasetImporter.SUPPORTED_DATASETS.items():
            datasets.append({
                "id": key,
                "name": config["path"],
                "description": config["description"],
                "task": config["task"],
                "languages": config["languages"],
                "size": "unknown",  # Would need to load to get size
                "license": "various",
                "source": "huggingface"
            })
        
        return datasets
    
    @staticmethod
    def import_dataset(
        dataset_id: str,
        split: str = "train",
        sample_size: Optional[int] = None,
        save_path: str = None
    ) -> Dict[str, Any]:
        """
        Import dataset from Hugging Face
        
        Args:
            dataset_id: Dataset identifier from SUPPORTED_DATASETS
            split: Which split to import (train, validation, test)
            sample_size: Number of samples to import (None for all)
            save_path: Where to save the imported dataset
            
        Returns:
            Dictionary with import results
        """
        if dataset_id not in HuggingFaceDatasetImporter.SUPPORTED_DATASETS:
            raise ValueError(f"Dataset {dataset_id} not supported")
        
        config = HuggingFaceDatasetImporter.SUPPORTED_DATASETS[dataset_id]
        
        try:
            logger.info(f"Loading dataset {dataset_id} from Hugging Face...")
            
            # Load dataset
            if dataset_id == "multi_lexsum":
                dataset = load_dataset(config["path"], name=config["name"], split=split)
            else:
                dataset = load_dataset(config["path"], split=split)
            
            # Convert to list of dictionaries
            data = []
            total_samples = len(dataset)
            
            # Determine how many samples to take
            if sample_size and sample_size < total_samples:
                indices = range(sample_size)
            else:
                indices = range(total_samples)
                sample_size = total_samples
            
            # Convert to our format
            for idx in indices:
                sample = dataset[idx]
                formatted_sample = HuggingFaceDatasetImporter._format_sample(
                    sample, config, dataset_id
                )
                if formatted_sample:
                    data.append(formatted_sample)
            
            # Save if path provided
            if save_path:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                "dataset_id": dataset_id,
                "dataset_name": config["path"],
                "imported_samples": len(data),
                "total_samples": total_samples,
                "config": config,
                "save_path": save_path,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error importing dataset {dataset_id}: {e}")
            return {
                "dataset_id": dataset_id,
                "status": "failed",
                "error": str(e)
            }
    
    @staticmethod
    def _format_sample(sample: Dict, config: Dict, dataset_id: str) -> Optional[Dict]:
        """Format sample to our standard format"""
        try:
            formatted = {
                "source_dataset": dataset_id,
                "imported_at": datetime.utcnow().isoformat()
            }
            
            # Map fields based on dataset type
            if dataset_id == "wikilarge":
                formatted.update({
                    "text": sample.get("original", ""),
                    "simplified": sample.get("simplification", ""),
                    "summary": sample.get("simplification", "")[:200]  # Truncate for summary
                })
            elif dataset_id == "xsum":
                formatted.update({
                    "text": sample.get("document", ""),
                    "summary": sample.get("summary", ""),
                    "simplified": sample.get("summary", "")
                })
            elif dataset_id == "cnn_dailymail":
                formatted.update({
                    "text": sample.get("article", ""),
                    "summary": sample.get("highlights", ""),
                    "simplified": sample.get("highlights", "")
                })
            elif dataset_id == "samsum":
                formatted.update({
                    "text": sample.get("dialogue", ""),
                    "summary": sample.get("summary", ""),
                    "simplified": sample.get("summary", "")
                })
            elif dataset_id == "caselaw":
                formatted.update({
                    "text": sample.get("text", ""),
                    "summary": sample.get("summary", ""),
                    "category": "legal"
                })
            elif dataset_id == "multi_lexsum":
                # Handle multi_lexsum specific format
                sources = sample.get("sources", [])
                if isinstance(sources, list) and sources:
                    # Concatenate all source documents
                    text = " ".join(sources)
                else:
                    text = str(sources) if sources else ""
                
                # Use the long summary as primary, fallback to short or tiny
                summary = (
                    sample.get("summary/long", "") or 
                    sample.get("summary/short", "") or 
                    sample.get("summary/tiny", "")
                )
                
                formatted.update({
                    "text": text,
                    "summary": summary,
                    "summary_long": sample.get("summary/long", ""),
                    "summary_short": sample.get("summary/short", ""),
                    "summary_tiny": sample.get("summary/tiny", ""),
                    "category": "legal",
                    "sources_count": len(sources) if isinstance(sources, list) else 1
                })
            else:
                # Generic format for other datasets
                formatted.update({
                    "text": str(sample.get("text", sample.get("document", sample.get("original", "")))),
                    "summary": str(sample.get("summary", sample.get("labels", ""))),
                    "metadata": sample
                })
            
            # Ensure required fields
            if not formatted.get("text") or len(formatted["text"]) < 10:
                return None
            
            return formatted
            
        except Exception as e:
            logger.warning(f"Error formatting sample: {e}")
            return None
    
    @staticmethod
    def search_datasets(query: str, task: str = None) -> List[Dict[str, Any]]:
        """Search for datasets by query and task"""
        results = []
        
        for key, config in HuggingFaceDatasetImporter.SUPPORTED_DATASETS.items():
            matches_query = (
                query.lower() in key.lower() or
                query.lower() in config["description"].lower() or
                query.lower() in config["path"].lower()
            )
            
            matches_task = task is None or config["task"] == task
            
            if matches_query and matches_task:
                results.append({
                    "id": key,
                    "name": config["path"],
                    "description": config["description"],
                    "task": config["task"],
                    "languages": config["languages"]
                })
        
        return results
    
    @staticmethod
    def get_dataset_info(dataset_id: str) -> Dict[str, Any]:
        """Get detailed information about a dataset"""
        if dataset_id not in HuggingFaceDatasetImporter.SUPPORTED_DATASETS:
            raise ValueError(f"Dataset {dataset_id} not found")
        
        config = HuggingFaceDatasetImporter.SUPPORTED_DATASETS[dataset_id]
        
        try:
            # Load a small sample to get stats
            if dataset_id == "multi_lexsum":
                dataset = load_dataset(config["path"], name=config["name"], split="train[:100]")
            else:
                dataset = load_dataset(config["path"], split="train[:100]")
            
            # Calculate basic statistics
            stats = {
                "sample_count": len(dataset),
                "fields": list(dataset.features.keys()),
                "example": dataset[0] if len(dataset) > 0 else None
            }
            
            return {
                **config,
                "stats": stats,
                "supported_splits": ["train", "validation", "test"],
                "estimated_size": "medium"  # Could be more sophisticated
            }
            
        except Exception as e:
            logger.warning(f"Could not load dataset for stats: {e}")
            return config