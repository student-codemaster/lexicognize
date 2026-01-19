from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os
from app.utils.evaluator import ROUGEEvaluator, BLEUEvaluator

router = APIRouter()

class EvaluationRequest(BaseModel):
    model_path: str
    dataset_name: str
    task: str  # "summarization" or "simplification"
    metrics: List[str] = ["rouge", "bleu"]

@router.post("/")
async def evaluate_model(request: EvaluationRequest):
    """Evaluate model performance"""
    
    # Check if model exists
    if not os.path.exists(request.model_path):
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Load dataset
    dataset_path = f"./data/uploads/{request.dataset_name}"
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    results = {}
    
    # Initialize evaluators
    if "rouge" in request.metrics:
        rouge_evaluator = ROUGEEvaluator()
        rouge_scores = rouge_evaluator.evaluate(
            model_path=request.model_path,
            dataset=dataset,
            task=request.task
        )
        results["rouge"] = rouge_scores
    
    if "bleu" in request.metrics:
        bleu_evaluator = BLEUEvaluator()
        bleu_scores = bleu_evaluator.evaluate(
            model_path=request.model_path,
            dataset=dataset,
            task=request.task
        )
        results["bleu"] = bleu_scores
    
    return {
        "task": request.task,
        "metrics": results,
        "dataset": request.dataset_name
    }

@router.get("/compare")
async def compare_models(model_paths: List[str], dataset_name: str):
    """Compare multiple models"""
    results = {}
    
    for model_path in model_paths:
        if os.path.exists(model_path):
            # Load and evaluate each model
            eval_request = EvaluationRequest(
                model_path=model_path,
                dataset_name=dataset_name,
                task="summarization"  # Adjust based on your needs
            )
            results[model_path] = await evaluate_model(eval_request)
    
    return results