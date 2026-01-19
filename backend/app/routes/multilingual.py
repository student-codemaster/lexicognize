from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import uuid
from datetime import datetime

from app.models.multilingual_trainer import MultilingualTrainer
from app.utils.language_utils import LanguageUtils

router = APIRouter()

class MultilingualTrainingRequest(BaseModel):
    dataset_name: str
    languages: List[str] = ['en', 'hi', 'ta', 'kn']
    epochs: int = 5
    batch_size: int = 4
    learning_rate: float = 5e-5
    model_name: str = "multilingual_legal_model"

class MultilingualGenerationRequest(BaseModel):
    text: str
    target_language: str = 'en'
    source_language: Optional[str] = None
    max_length: int = 256

@router.post("/train")
async def train_multilingual_model(
    request: MultilingualTrainingRequest,
    background_tasks: BackgroundTasks
):
    """Start multilingual model training"""
    try:
        # Load dataset
        dataset_path = f"data/datasets/{request.dataset_name}.json"
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        # Create trainer
        trainer = MultilingualTrainer(base_model="facebook/mbart-large-50")
        
        # Prepare data
        train_data, val_data = trainer.prepare_multilingual_data(
            data,
            target_languages=request.languages
        )
        
        # Create output directory
        output_dir = f"data/models/{request.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Start training in background
        job_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            run_multilingual_training,
            job_id,
            trainer,
            train_data,
            val_data,
            output_dir,
            request
        )
        
        return {
            "job_id": job_id,
            "message": "Multilingual training started",
            "output_dir": output_dir,
            "languages": request.languages,
            "training_samples": len(train_data),
            "validation_samples": len(val_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@router.post("/generate")
async def generate_multilingual(request: MultilingualGenerationRequest):
    """Generate text in target language"""
    try:
        # Load latest multilingual model
        models_dir = "data/models"
        multilingual_models = []
        
        for model_name in os.listdir(models_dir):
            model_path = os.path.join(models_dir, model_name)
            metadata_path = os.path.join(model_path, "metadata.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get("model_type") == "multilingual":
                    multilingual_models.append({
                        "name": model_name,
                        "path": model_path,
                        "created_at": metadata.get("created_at"),
                        "languages": metadata.get("languages", [])
                    })
        
        if not multilingual_models:
            raise HTTPException(status_code=404, detail="No multilingual models found")
        
        # Use latest model
        latest_model = max(multilingual_models, key=lambda x: x["created_at"])
        
        # Load model
        trainer = MultilingualTrainer()
        trainer.tokenizer = AutoTokenizer.from_pretrained(latest_model["path"])
        trainer.model = AutoModelForSeq2SeqLM.from_pretrained(latest_model["path"])
        trainer.model.to(trainer.device)
        
        # Generate
        result = trainer.generate_multilingual(
            request.text,
            request.target_language,
            request.source_language,
            request.max_length
        )
        
        result['model_used'] = latest_model["name"]
        result['supported_languages'] = latest_model["languages"]
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@router.get("/models")
async def list_multilingual_models():
    """List all multilingual models"""
    try:
        models_dir = "data/models"
        multilingual_models = []
        
        for model_name in os.listdir(models_dir):
            model_path = os.path.join(models_dir, model_name)
            metadata_path = os.path.join(model_path, "metadata.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get("model_type") == "multilingual":
                    multilingual_models.append({
                        "name": model_name,
                        "path": model_path,
                        "created_at": metadata.get("created_at"),
                        "languages": metadata.get("languages", []),
                        "training_samples": metadata.get("training_samples"),
                        "validation_samples": metadata.get("validation_samples"),
                        "metrics": metadata.get("metrics", {})
                    })
        
        return {
            "models": multilingual_models,
            "count": len(multilingual_models)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

@router.post("/translate-and-summarize")
async def translate_and_summarize(
    text: str,
    target_language: str,
    source_language: str = None,
    max_summary_length: int = 200
):
    """Translate text and generate summary in target language"""
    try:
        from app.utils.translator import LegalTranslator
        from app.models.multilingual_trainer import MultilingualTrainer
        
        translator = LegalTranslator()
        
        # Detect language if not specified
        if source_language is None:
            source_language, confidence = LanguageUtils.detect_language(text)
        
        # Translate text
        if source_language != target_language:
            translated_text = translator.translate_text(
                text,
                source_language,
                target_language,
                max_length=1024
            )
        else:
            translated_text = text
        
        # Load multilingual model for summarization
        models = await list_multilingual_models()
        if not models["models"]:
            return {
                "translated_text": translated_text,
                "summary": "No multilingual model available for summarization",
                "translation_only": True
            }
        
        # Use latest model
        latest_model = max(models["models"], key=lambda x: x["created_at"])
        
        trainer = MultilingualTrainer()
        trainer.tokenizer = AutoTokenizer.from_pretrained(latest_model["path"])
        trainer.model = AutoModelForSeq2SeqLM.from_pretrained(latest_model["path"])
        trainer.model.to(trainer.device)
        
        # Generate summary in target language
        summary_result = trainer.generate_multilingual(
            translated_text,
            target_language,
            target_language,  # Source and target same for summarization
            max_summary_length
        )
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "summary": summary_result["generated_text"],
            "source_language": source_language,
            "target_language": target_language,
            "model_used": latest_model["name"],
            "translation_needed": source_language != target_language
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in translate and summarize: {str(e)}")

async def run_multilingual_training(
    job_id: str,
    trainer: MultilingualTrainer,
    train_data: List[Dict],
    val_data: List[Dict],
    output_dir: str,
    request: MultilingualTrainingRequest
):
    """Run multilingual training in background"""
    try:
        # Training logic here
        metrics = trainer.train(
            train_data=train_data,
            val_data=val_data,
            output_dir=output_dir,
            languages=request.languages,
            epochs=request.epochs,
            batch_size=request.batch_size,
            learning_rate=request.learning_rate
        )
        
        logger.info(f"Multilingual training job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Multilingual training job {job_id} failed: {e}")