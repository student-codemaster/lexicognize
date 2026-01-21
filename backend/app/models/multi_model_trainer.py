import os
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments
)
from datasets import Dataset as HFDataset
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import evaluate

logger = logging.getLogger(__name__)

class MultiTaskDataset(Dataset):
    """Dataset for both summarization and simplification tasks"""
    
    def __init__(self, data: List[Dict], tokenizer, max_length: int = 1024, task: str = "both"):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.task = task  # "summary", "simplify", or "both"
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        if self.task == "summary":
            source = item.get("text", "")
            target = item.get("summary", "")
        elif self.task == "simplification":
            source = item.get("text", "")
            target = item.get("simplified", item.get("summary", ""))
        else:  # both - alternate between tasks
            source = item.get("text", "")
            if idx % 2 == 0:
                target = item.get("summary", "")
            else:
                target = item.get("simplified", item.get("summary", ""))
        
        # Tokenize inputs
        inputs = self.tokenizer(
            source,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Tokenize targets
        targets = self.tokenizer(
            target,
            max_length=256,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": inputs["input_ids"].squeeze(),
            "attention_mask": inputs["attention_mask"].squeeze(),
            "labels": targets["input_ids"].squeeze()
        }

class MultiModelTrainer:
    """Trainer for both BART and PEGASUS models"""
    
    def __init__(self, model_type: str = "bart", task: str = "both"):
        self.model_type = model_type
        self.task = task
        
        # Set model names based on type
        if model_type.lower() == "bart":
            self.model_name = "facebook/bart-large"
        elif model_type.lower() == "pegasus":
            self.model_name = "google/pegasus-large"
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def prepare_data(self, data: List[Dict], train_ratio: float = 0.8) -> Tuple:
        """Prepare data for training and validation"""
        # Split data
        split_idx = int(len(data) * train_ratio)
        train_data = data[:split_idx]
        val_data = data[split_idx:]
        
        logger.info(f"Data split: {len(train_data)} training, {len(val_data)} validation samples")
        
        return train_data, val_data
    
    def train(
        self,
        train_data: List[Dict],
        val_data: List[Dict],
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 5e-5,
        max_length: int = 1024,
        target_max_length: int = 256,
        save_steps: int = 500,
        eval_steps: int = 500,
        logging_steps: int = 100
    ) -> Dict[str, Any]:
        """Train the model"""
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        
        # Create datasets
        train_dataset = MultiTaskDataset(
            train_data, self.tokenizer, max_length, self.task
        )
        val_dataset = MultiTaskDataset(
            val_data, self.tokenizer, max_length, self.task
        )
        
        # Convert to HuggingFace datasets
        hf_train_dataset = HFDataset.from_dict({
            "input_ids": [item["input_ids"].tolist() for item in train_dataset],
            "attention_mask": [item["attention_mask"].tolist() for item in train_dataset],
            "labels": [item["labels"].tolist() for item in train_dataset]
        })
        
        hf_val_dataset = HFDataset.from_dict({
            "input_ids": [item["input_ids"].tolist() for item in val_dataset],
            "attention_mask": [item["attention_mask"].tolist() for item in val_dataset],
            "labels": [item["labels"].tolist() for item in val_dataset]
        })
        
        # Setup training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=logging_steps,
            save_steps=save_steps,
            eval_steps=eval_steps,
            evaluation_strategy="steps",
            save_total_limit=2,
            load_best_model_at_end=True,
            predict_with_generate=True,
            fp16=torch.cuda.is_available(),
            report_to="tensorboard",
            learning_rate=learning_rate,
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)
        
        # Metrics
        rouge = evaluate.load("rouge")
        bleu = evaluate.load("bleu")
        
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            decoded_preds = self.tokenizer.batch_decode(predictions, skip_special_tokens=True)
            
            # Replace -100 in the labels as we can't decode them
            labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
            decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)
            
            # Compute ROUGE scores
            rouge_result = rouge.compute(
                predictions=decoded_preds,
                references=decoded_labels,
                use_stemmer=True
            )
            
            # Compute BLEU score
            bleu_result = bleu.compute(
                predictions=decoded_preds,
                references=[[ref] for ref in decoded_labels]
            )
            
            result = {key: value for key, value in rouge_result.items()}
            result["bleu"] = bleu_result["bleu"]
            
            return {k: round(v, 4) for k, v in result.items()}
        
        # Create trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=hf_train_dataset,
            eval_dataset=hf_val_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics
        )
        
        # Train the model
        logger.info("Starting training...")
        train_result = trainer.train()
        
        # Save the model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save training metrics
        metrics = train_result.metrics
        metrics_path = os.path.join(output_dir, "training_metrics.json")
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        # Save metadata
        metadata = {
            "model_type": self.model_type,
            "task": self.task,
            "training_data_size": len(train_data),
            "validation_data_size": len(val_data),
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "max_length": max_length,
            "target_max_length": target_max_length,
            "created_at": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Training completed. Model saved to {output_dir}")
        
        return metrics
    
    def evaluate(self, test_data: List[Dict], model_path: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate the model on test data"""
        if model_path:
            model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            tokenizer = AutoTokenizer.from_pretrained(model_path)
        else:
            model = self.model
            tokenizer = self.tokenizer
        
        model.to(self.device)
        model.eval()
        
        # Load metrics
        rouge = evaluate.load("rouge")
        bleu = evaluate.load("bleu")
        
        all_predictions = []
        all_references = []
        
        # Create dataset
        test_dataset = MultiTaskDataset(test_data, tokenizer, task=self.task)
        
        # Create dataloader
        dataloader = DataLoader(test_dataset, batch_size=4, shuffle=False)
        
        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                
                # Generate predictions
                outputs = model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    max_length=256,
                    num_beams=4,
                    temperature=1.0,
                    do_sample=False
                )
                
                # Decode predictions
                predictions = tokenizer.batch_decode(outputs, skip_special_tokens=True)
                
                # Decode references
                ref_labels = torch.where(labels != -100, labels, tokenizer.pad_token_id)
                references = tokenizer.batch_decode(ref_labels, skip_special_tokens=True)
                
                all_predictions.extend(predictions)
                all_references.extend(references)
        
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
        
        results = {
            "rouge": {k: v for k, v in rouge_scores.items()},
            "bleu": bleu_scores["bleu"],
            "sample_count": len(test_data),
            "predictions": all_predictions[:5],  # First 5 predictions as sample
            "references": all_references[:5]      # First 5 references as sample
        }
        
        return results
    
    def generate_summary(self, text: str, model_path: Optional[str] = None, max_length: int = 256) -> str:
        """Generate summary for a single text"""
        if model_path:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        else:
            model = self.model
            tokenizer = self.tokenizer
        
        model.to(self.device)
        model.eval()
        
        # Tokenize input
        inputs = tokenizer(
            text,
            max_length=1024,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate summary
        with torch.no_grad():
            outputs = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                num_beams=4,
                temperature=1.0,
                do_sample=False,
                early_stopping=True
            )
        
        # Decode summary
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary