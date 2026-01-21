from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
import torch
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.session import get_db
from app.auth.security import get_current_user
from app.auth.schemas import UserInDB
from app.auth import crud as auth_crud
from app.models.multi_model_trainer import MultiModelTrainer
from app.models.bart_trainer import BARTTrainer
from app.models.pegasus_trainer import PEGASUSTrainer
from app.models.multilingual_trainer import MultilingualTrainer
from app.utils.data_processor import LegalDataProcessor

router = APIRouter()

class InferenceRequest(BaseModel):
    text: str
    model_path: str
    model_type: str  # "bart", "pegasus", "multilingual", "multi"
    task: str = "summarization"  # "summarization", "simplification"
    max_length: int = 256
    num_beams: int = 4
    temperature: float = 1.0
    do_sample: bool = False

class BatchInferenceRequest(BaseModel):
    texts: List[str]
    model_path: str
    model_type: str
    task: str = "summarization"
    max_length: int = 256
    num_beams: int = 4
    temperature: float = 1.0
    do_sample: bool = False

class InferenceResponse(BaseModel):
    summary: str
    confidence: Optional[float] = None
    processing_time: float
    model_info: Dict[str, Any]

class BatchInferenceResponse(BaseModel):
    results: List[InferenceResponse]
    total_processing_time: float
    model_info: Dict[str, Any]

@router.post("/generate", response_model=InferenceResponse)
async def generate_summary(
    request: InferenceRequest,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summary for a single text"""
    start_time = datetime.now()
    
    try:
        # Validate model access
        model = auth_crud.get_user_model_by_path(db, request.model_path, current_user.id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Model not found or access denied"
            )
        
        # Check if model file exists
        if not os.path.exists(request.model_path):
            raise HTTPException(
                status_code=404,
                detail="Model file not found"
            )
        
        # Initialize appropriate trainer
        trainer = _get_trainer(request.model_type, request.model_path)
        
        # Generate summary
        if hasattr(trainer, 'generate_summary'):
            summary = trainer.generate_summary(
                text=request.text,
                model_path=request.model_path,
                max_length=request.max_length
            )
        else:
            # Fallback to generic generation
            summary = _generate_with_generic_trainer(
                trainer, request.text, request.model_path, request
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return InferenceResponse(
            summary=summary,
            processing_time=processing_time,
            model_info={
                "model_type": request.model_type,
                "model_path": request.model_path,
                "task": request.task,
                "model_name": model.name
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

@router.post("/batch", response_model=BatchInferenceResponse)
async def batch_generate_summary(
    request: BatchInferenceRequest,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summaries for multiple texts"""
    start_time = datetime.now()
    
    try:
        # Validate model access
        model = auth_crud.get_user_model_by_path(db, request.model_path, current_user.id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Model not found or access denied"
            )
        
        # Check if model file exists
        if not os.path.exists(request.model_path):
            raise HTTPException(
                status_code=404,
                detail="Model file not found"
            )
        
        # Initialize trainer
        trainer = _get_trainer(request.model_type, request.model_path)
        
        results = []
        
        # Process each text
        for i, text in enumerate(request.texts):
            text_start_time = datetime.now()
            
            try:
                if hasattr(trainer, 'generate_summary'):
                    summary = trainer.generate_summary(
                        text=text,
                        model_path=request.model_path,
                        max_length=request.max_length
                    )
                else:
                    summary = _generate_with_generic_trainer(
                        trainer, text, request.model_path, request
                    )
                
                processing_time = (datetime.now() - text_start_time).total_seconds()
                
                results.append(InferenceResponse(
                    summary=summary,
                    processing_time=processing_time,
                    model_info={
                        "model_type": request.model_type,
                        "model_path": request.model_path,
                        "task": request.task,
                        "model_name": model.name
                    }
                ))
                
            except Exception as e:
                # Add error result for this text
                processing_time = (datetime.now() - text_start_time).total_seconds()
                results.append(InferenceResponse(
                    summary=f"Error: {str(e)}",
                    processing_time=processing_time,
                    model_info={
                        "model_type": request.model_type,
                        "model_path": request.model_path,
                        "task": request.task,
                        "error": True
                    }
                ))
        
        total_processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchInferenceResponse(
            results=results,
            total_processing_time=total_processing_time,
            model_info={
                "model_type": request.model_type,
                "model_path": request.model_path,
                "task": request.task,
                "model_name": model.name,
                "total_texts": len(request.texts)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch processing: {str(e)}"
        )

@router.post("/evaluate")
async def evaluate_model(
    model_path: str,
    test_data_path: str,
    model_type: str,
    task: str = "summarization",
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Evaluate a trained model on test data"""
    try:
        # Validate model access
        model = auth_crud.get_user_model_by_path(db, model_path, current_user.id)
        if not model:
            raise HTTPException(
                status_code=404,
                detail="Model not found or access denied"
            )
        
        # Check if test data exists and user has access
        if not os.path.exists(test_data_path):
            raise HTTPException(
                status_code=404,
                detail="Test data file not found"
            )
        
        # Load test data
        with open(test_data_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Initialize trainer
        trainer = _get_trainer(model_type, model_path)
        
        # Evaluate model
        if hasattr(trainer, 'evaluate'):
            results = trainer.evaluate(
                test_data=test_data,
                model_path=model_path,
                task=task
            )
        else:
            # Fallback evaluation
            results = _evaluate_with_generic_trainer(
                trainer, test_data, model_path, task
            )
        
        # Save evaluation results
        evaluation_record = auth_crud.create_evaluation_result(db, {
            'user_id': current_user.id,
            'model_id': model.id,
            'test_data_path': test_data_path,
            'results': results,
            'task': task,
            'created_at': datetime.now().isoformat()
        })
        
        return {
            "evaluation_id": evaluation_record.id,
            "model_info": {
                "model_type": model_type,
                "model_path": model_path,
                "model_name": model.name
            },
            "test_data_info": {
                "test_data_path": test_data_path,
                "sample_count": len(test_data)
            },
            "results": results,
            "created_at": evaluation_record.created_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error evaluating model: {str(e)}"
        )

@router.get("/models")
async def get_available_models(
    model_type: Optional[str] = None,
    task: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available trained models for inference"""
    models = auth_crud.get_user_models(
        db, current_user.id, model_type=model_type, task=task
    )
    
    # Add model file existence check
    available_models = []
    for model in models:
        if os.path.exists(model.model_path):
            # Check for required model files
            model_files = os.listdir(model.model_path)
            has_required_files = any(
                file.endswith('.bin') or file.endswith('.safetensors') 
                for file in model_files
            )
            
            if has_required_files:
                available_models.append({
                    "id": model.id,
                    "name": model.name,
                    "description": model.description,
                    "model_type": model.model_type,
                    "task": model.task,
                    "model_path": model.model_path,
                    "created_at": model.created_at,
                    "metadata": model.metadata
                })
    
    return {
        "models": available_models,
        "total": len(available_models)
    }

@router.get("/history")
async def get_inference_history(
    skip: int = 0,
    limit: int = 50,
    model_id: Optional[int] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get inference history for current user"""
    history = auth_crud.get_user_inference_history(
        db, current_user.id, skip=skip, limit=limit, model_id=model_id
    )
    
    total = auth_crud.count_user_inference_history(
        db, current_user.id, model_id=model_id
    )
    
    return {
        "history": history,
        "total": total,
        "skip": skip,
        "limit": limit
    }

def _get_trainer(model_type: str, model_path: str):
    """Get appropriate trainer based on model type"""
    if model_type.lower() == "bart":
        return BARTTrainer()
    elif model_type.lower() == "pegasus":
        return PEGASUSTrainer()
    elif model_type.lower() == "multilingual":
        return MultilingualTrainer()
    elif model_type.lower() == "multi":
        return MultiModelTrainer()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

def _generate_with_generic_trainer(trainer, text: str, model_path: str, request):
    """Fallback generation using generic trainer"""
    try:
        # Load model and tokenizer
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        # Tokenize input
        inputs = tokenizer(
            text,
            max_length=1024,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate summary
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=request.max_length,
                num_beams=request.num_beams,
                temperature=request.temperature,
                do_sample=request.do_sample,
                early_stopping=True
            )
        
        # Decode summary
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
        
    except Exception as e:
        raise Exception(f"Generic generation failed: {str(e)}")

def _evaluate_with_generic_trainer(trainer, test_data: List[Dict], model_path: str, task: str):
    """Fallback evaluation using generic approach"""
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import evaluate
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        # Load metrics
        rouge = evaluate.load("rouge")
        bleu = evaluate.load("bleu")
        
        all_predictions = []
        all_references = []
        
        for sample in test_data:
            text = sample.get("text", "")
            reference = sample.get("summary", sample.get("simplified", ""))
            
            if not text or not reference:
                continue
            
            # Tokenize input
            inputs = tokenizer(
                text,
                max_length=1024,
                padding="max_length",
                truncation=True,
                return_tensors="pt"
            )
            
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate prediction
            with torch.no_grad():
                outputs = model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=256,
                    num_beams=4,
                    temperature=1.0,
                    do_sample=False
                )
            
            # Decode prediction
            prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            all_predictions.append(prediction)
            all_references.append(reference)
        
        # Compute metrics
        rouge_scores = rouge.compute(
            predictions=all_predictions,
            references=all_references,
            use_stemmer=True
        )
        
        bleu_scores = bleu.compute(
            predictions=all_predictions,
            references=[[ref] for ref in all_references]
        )
        
        return {
            "rouge": {k: v for k, v in rouge_scores.items()},
            "bleu": bleu_scores["bleu"],
            "sample_count": len(all_predictions),
            "predictions": all_predictions[:5],
            "references": all_references[:5]
        }
        
    except Exception as e:
        raise Exception(f"Generic evaluation failed: {str(e)}")