import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)
from datasets import Dataset as HFDataset
import json
import os
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

from app.utils.translator import LegalTranslator
from app.utils.language_utils import LanguageUtils

logger = logging.getLogger(__name__)

class MultilingualLegalDataset(Dataset):
    """Dataset for multilingual legal text"""
    
    def __init__(self, data: List[Dict], tokenizer, languages: List[str] = None):
        self.data = data
        self.tokenizer = tokenizer
        self.languages = languages or ['en', 'hi', 'ta', 'kn']
        self.translator = LegalTranslator()
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Original English text
        english_text = item.get('text', '')
        english_summary = item.get('summary', '')
        
        # Randomly select target language
        import random
        target_lang = random.choice(self.languages)
        
        if target_lang != 'en':
            try:
                # Translate to target language
                translated_text = self.translator.translate_text(
                    english_text, 'en', target_lang
                )
                translated_summary = self.translator.translate_text(
                    english_summary, 'en', target_lang
                )
                
                # Use translated text
                source_text = english_text  # Keep English as source for now
                target_text = translated_summary
                
                # Add language tags
                source_text = f"[{target_lang.upper()}] {source_text}"
                target_text = f"[{target_lang.upper()}] {target_text}"
                
            except Exception as e:
                logger.error(f"Translation error: {e}")
                # Fallback to English
                source_text = english_text
                target_text = english_summary
        else:
            source_text = english_text
            target_text = english_summary
        
        # Tokenize
        inputs = self.tokenizer(
            source_text,
            max_length=1024,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        targets = self.tokenizer(
            target_text,
            max_length=256,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": inputs["input_ids"].squeeze(),
            "attention_mask": inputs["attention_mask"].squeeze(),
            "labels": targets["input_ids"].squeeze(),
            "language": target_lang
        }

class MultilingualTrainer:
    """Trainer for multilingual models"""
    
    def __init__(self, base_model: str = "facebook/mbart-large-50"):
        self.base_model = base_model
        self.tokenizer = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def prepare_multilingual_data(
        self,
        data: List[Dict],
        target_languages: List[str] = None,
        augmentation_ratio: float = 0.3
    ) -> Tuple[List[Dict], List[Dict]]:
        """Prepare multilingual training data with augmentation"""
        
        if target_languages is None:
            target_languages = ['hi', 'ta', 'kn']  # Hindi, Tamil, Kannada
        
        augmented_data = []
        translator = LegalTranslator()
        
        for item in data:
            english_text = item.get('text', '')
            english_summary = item.get('summary', '')
            
            if not english_text or not english_summary:
                continue
            
            # Add original English
            augmented_data.append({
                'text': english_text,
                'summary': english_summary,
                'language': 'en',
                'original': True
            })
            
            # Add translations to other languages
            for lang in target_languages:
                try:
                    translated_text = translator.translate_text(
                        english_text, 'en', lang
                    )
                    translated_summary = translator.translate_text(
                        english_summary, 'en', lang
                    )
                    
                    augmented_data.append({
                        'text': translated_text,
                        'summary': translated_summary,
                        'language': lang,
                        'original': False,
                        'source_language': 'en'
                    })
                except Exception as e:
                    logger.error(f"Error translating to {lang}: {e}")
        
        # Split into train/validation
        split_idx = int(len(augmented_data) * 0.8)
        train_data = augmented_data[:split_idx]
        val_data = augmented_data[split_idx:]
        
        logger.info(f"Multilingual dataset created:")
        logger.info(f"  Total samples: {len(augmented_data)}")
        logger.info(f"  Train samples: {len(train_data)}")
        logger.info(f"  Validation samples: {len(val_data)}")
        
        # Count by language
        lang_counts = {}
        for item in augmented_data:
            lang = item['language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        
        logger.info(f"  Language distribution: {lang_counts}")
        
        return train_data, val_data
    
    def train(
        self,
        train_data: List[Dict],
        val_data: List[Dict],
        output_dir: str,
        languages: List[str] = None,
        epochs: int = 5,
        batch_size: int = 4,
        learning_rate: float = 5e-5,
        max_length: int = 1024,
        target_max_length: int = 256
    ) -> Dict:
        """Train multilingual model"""
        
        if languages is None:
            languages = ['en', 'hi', 'ta', 'kn']
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        
        # Add special tokens for language tags
        special_tokens = [f"[{lang.upper()}]" for lang in languages]
        self.tokenizer.add_special_tokens({'additional_special_tokens': special_tokens})
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.base_model)
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.to(self.device)
        
        # Create datasets
        train_dataset = MultilingualLegalDataset(train_data, self.tokenizer, languages)
        val_dataset = MultilingualLegalDataset(val_data, self.tokenizer, languages)
        
        # Convert to HuggingFace datasets
        hf_train = HFDataset.from_dict({
            'input_ids': [item['input_ids'].tolist() for item in train_dataset],
            'attention_mask': [item['attention_mask'].tolist() for item in train_dataset],
            'labels': [item['labels'].tolist() for item in train_dataset]
        })
        
        hf_val = HFDataset.from_dict({
            'input_ids': [item['input_ids'].tolist() for item in val_dataset],
            'attention_mask': [item['attention_mask'].tolist() for item in val_dataset],
            'labels': [item['labels'].tolist() for item in val_dataset]
        })
        
        # Training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            save_steps=500,
            eval_steps=500,
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
        
        # Trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=hf_train,
            eval_dataset=hf_val,
            data_collator=data_collator,
            tokenizer=self.tokenizer
        )
        
        # Train
        logger.info("Starting multilingual training...")
        train_result = trainer.train()
        
        # Save model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save metadata
        metadata = {
            "model_type": "multilingual",
            "base_model": self.base_model,
            "languages": languages,
            "training_samples": len(train_data),
            "validation_samples": len(val_data),
            "epochs": epochs,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "max_length": max_length,
            "target_max_length": target_max_length,
            "created_at": datetime.now().isoformat(),
            "metrics": train_result.metrics
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Multilingual training completed. Model saved to {output_dir}")
        
        return train_result.metrics
    
    def generate_multilingual(
        self,
        text: str,
        target_language: str = 'en',
        source_language: str = None,
        max_length: int = 256
    ) -> Dict:
        """Generate text in target language"""
        
        if source_language is None:
            # Auto-detect source language
            source_language, _ = LanguageUtils.detect_language(text)
        
        # Add language tag
        if source_language != 'en':
            # Translate to English first if needed
            translator = LegalTranslator()
            english_text = translator.translate_text(text, source_language, 'en')
            tagged_text = f"[{target_language.upper()}] {english_text}"
        else:
            tagged_text = f"[{target_language.upper()}] {text}"
        
        # Tokenize
        inputs = self.tokenizer(
            tagged_text,
            return_tensors="pt",
            max_length=1024,
            truncation=True
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                temperature=0.7,
                do_sample=True
            )
        
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove language tag if present
        if generated.startswith(f"[{target_language.upper()}]"):
            generated = generated[len(f"[{target_language.upper()}]"):].strip()
        
        return {
            'original_text': text,
            'generated_text': generated,
            'source_language': source_language,
            'target_language': target_language,
            'tagged_input': tagged_text
        }