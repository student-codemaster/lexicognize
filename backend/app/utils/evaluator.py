from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import numpy as np
from typing import List, Dict, Any

class ROUGEEvaluator:
    def __init__(self):
        self.scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    def evaluate(self, model_path: str, dataset: List[Dict], task: str) -> Dict[str, float]:
        """Evaluate model using ROUGE metrics"""
        # Load model
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        summarizer = pipeline(task, model=model, tokenizer=tokenizer)
        
        rouge_scores = []
        
        for item in dataset[:100]:  # Evaluate on subset
            source = item["text"]
            target = item["summary"] if task == "summarization" else item["simplified"]
            
            # Generate prediction
            prediction = summarizer(source, max_length=256, min_length=30, do_sample=False)[0]['summary_text']
            
            # Calculate ROUGE scores
            scores = self.scorer.score(target, prediction)
            rouge_scores.append({
                'rouge1': scores['rouge1'].fmeasure,
                'rouge2': scores['rouge2'].fmeasure,
                'rougeL': scores['rougeL'].fmeasure
            })
        
        # Calculate averages
        avg_scores = {
            'rouge1': np.mean([s['rouge1'] for s in rouge_scores]),
            'rouge2': np.mean([s['rouge2'] for s in rouge_scores]),
            'rougeL': np.mean([s['rougeL'] for s in rouge_scores])
        }
        
        return avg_scores

class BLEUEvaluator:
    def __init__(self):
        self.smooth = SmoothingFunction().method1
    
    def evaluate(self, model_path: str, dataset: List[Dict], task: str) -> Dict[str, float]:
        """Evaluate model using BLEU score"""
        # Load model
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        summarizer = pipeline(task, model=model, tokenizer=tokenizer)
        
        bleu_scores = []
        
        for item in dataset[:100]:  # Evaluate on subset
            source = item["text"]
            target = item["summary"] if task == "summarization" else item["simplified"]
            
            # Generate prediction
            prediction = summarizer(source, max_length=256, min_length=30, do_sample=False)[0]['summary_text']
            
            # Tokenize
            target_tokens = target.split()
            prediction_tokens = prediction.split()
            
            # Calculate BLEU score
            bleu = sentence_bleu(
                [target_tokens],
                prediction_tokens,
                smoothing_function=self.smooth
            )
            bleu_scores.append(bleu)
        
        return {
            'bleu': np.mean(bleu_scores),
            'bleu_std': np.std(bleu_scores)
        }

class ModelEvaluator:
    """Comprehensive model evaluator combining multiple metrics"""
    
    def __init__(self):
        self.rouge_evaluator = ROUGEEvaluator()
        self.bleu_evaluator = BLEUEvaluator()
    
    def evaluate_model(
        self, 
        model_path: str, 
        dataset: List[Dict], 
        task: str = "summarization",
        metrics: List[str] = ["rouge", "bleu"]
    ) -> Dict[str, Any]:
        """
        Comprehensive model evaluation
        
        Args:
            model_path: Path to trained model
            dataset: Test dataset
            task: Task type (summarization or simplification)
            metrics: List of metrics to compute
            
        Returns:
            Dictionary containing evaluation results
        """
        results = {
            "model_path": model_path,
            "task": task,
            "dataset_size": len(dataset),
            "evaluated_samples": min(len(dataset), 100),
            "metrics": {}
        }
        
        # Compute ROUGE scores
        if "rouge" in metrics:
            try:
                rouge_scores = self.rouge_evaluator.evaluate(model_path, dataset, task)
                results["metrics"]["rouge"] = rouge_scores
            except Exception as e:
                results["metrics"]["rouge"] = {"error": str(e)}
        
        # Compute BLEU scores
        if "bleu" in metrics:
            try:
                bleu_scores = self.bleu_evaluator.evaluate(model_path, dataset, task)
                results["metrics"]["bleu"] = bleu_scores
            except Exception as e:
                results["metrics"]["bleu"] = {"error": str(e)}
        
        return results
    
    def compare_models(
        self, 
        model_paths: List[str], 
        dataset: List[Dict], 
        task: str = "summarization"
    ) -> Dict[str, Any]:
        """
        Compare multiple models on the same dataset
        
        Args:
            model_paths: List of model paths to compare
            dataset: Test dataset
            task: Task type
            
        Returns:
            Comparison results
        """
        comparison = {
            "task": task,
            "dataset_size": len(dataset),
            "models": {}
        }
        
        for model_path in model_paths:
            model_name = model_path.split("/")[-1] if "/" in model_path else model_path
            results = self.evaluate_model(model_path, dataset, task)
            comparison["models"][model_name] = results
        
        # Find best model for each metric
        best_models = {}
        
        # Compare ROUGE scores
        rouge_scores = {}
        for model_name, results in comparison["models"].items():
            if "rouge" in results["metrics"] and "rouge1" in results["metrics"]["rouge"]:
                rouge_scores[model_name] = results["metrics"]["rouge"]["rouge1"]
        
        if rouge_scores:
            best_models["rouge1"] = max(rouge_scores, key=rouge_scores.get)
        
        # Compare BLEU scores
        bleu_scores = {}
        for model_name, results in comparison["models"].items():
            if "bleu" in results["metrics"] and "bleu" in results["metrics"]["bleu"]:
                bleu_scores[model_name] = results["metrics"]["bleu"]["bleu"]
        
        if bleu_scores:
            best_models["bleu"] = max(bleu_scores, key=bleu_scores.get)
        
        comparison["best_models"] = best_models
        
        return comparison