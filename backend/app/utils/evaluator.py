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