#!/usr/bin/env python3
"""
Test script to verify multi_lexsum dataset integration and model training pipeline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.utils.huggingface_importer import HuggingFaceDatasetImporter
from app.utils.data_processor import LegalDataProcessor
from app.models.bart_trainer import BARTTrainer
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_multi_lexsum_import():
    """Test importing multi_lexsum dataset"""
    logger.info("Testing multi_lexsum dataset import...")
    
    try:
        # Test dataset info
        info = HuggingFaceDatasetImporter.get_dataset_info("multi_lexsum")
        logger.info(f"Dataset info: {info}")
        
        # Test small import
        result = HuggingFaceDatasetImporter.import_dataset(
            dataset_id="multi_lexsum",
            split="validation[:10]",  # Just 10 samples for testing
            sample_size=5,
            save_path="test_multi_lexsum.json"
        )
        
        logger.info(f"Import result: {result}")
        
        if result["status"] == "success":
            # Load and inspect the imported data
            with open("test_multi_lexsum.json", 'r') as f:
                data = json.load(f)
            
            logger.info(f"Imported {len(data)} samples")
            
            if data:
                sample = data[0]
                logger.info(f"Sample keys: {list(sample.keys())}")
                logger.info(f"Text length: {len(sample.get('text', ''))}")
                logger.info(f"Summary length: {len(sample.get('summary', ''))}")
                logger.info(f"Sources count: {sample.get('sources_count', 'N/A')}")
                
                # Check if multi_lexsum specific fields are present
                if 'summary_long' in sample:
                    logger.info(f"Long summary: {sample['summary_long'][:100]}...")
                if 'summary_short' in sample:
                    logger.info(f"Short summary: {sample['summary_short'][:100]}...")
                if 'summary_tiny' in sample:
                    logger.info(f"Tiny summary: {sample['summary_tiny']}")
                
            return True, data
        else:
            logger.error(f"Import failed: {result.get('error', 'Unknown error')}")
            return False, None
            
    except Exception as e:
        logger.error(f"Error testing multi_lexsum import: {e}")
        return False, None

def test_data_processing(data):
    """Test data processing functionality"""
    logger.info("Testing data processing...")
    
    try:
        processor = LegalDataProcessor()
        
        # Process the dataset
        processed_data = processor.process_dataset(data)
        
        # Calculate statistics
        stats = processor.calculate_statistics(processed_data)
        
        logger.info(f"Processed {len(processed_data)} samples")
        logger.info(f"Validation rate: {stats.get('validation_rate', 0):.2f}%")
        logger.info(f"Languages: {stats.get('languages', {})}")
        logger.info(f"Categories: {stats.get('categories', {})}")
        
        if 'text_length_stats' in stats:
            tls = stats['text_length_stats']
            logger.info(f"Text length - Mean: {tls.get('mean', 0):.1f}, "
                       f"Min: {tls.get('min', 0)}, Max: {tls.get('max', 0)}")
        
        if 'summary_length_stats' in stats:
            sls = stats['summary_length_stats']
            logger.info(f"Summary length - Mean: {sls.get('mean', 0):.1f}, "
                       f"Min: {sls.get('min', 0)}, Max: {sls.get('max', 0)}")
        
        return True, processed_data
        
    except Exception as e:
        logger.error(f"Error in data processing: {e}")
        return False, None

def test_bart_trainer(data):
    """Test BART trainer with a small subset"""
    logger.info("Testing BART trainer...")
    
    try:
        # Filter valid samples
        valid_data = [sample for sample in data if sample.get('is_valid', True)]
        
        if len(valid_data) < 2:
            logger.warning("Not enough valid samples for training test")
            return False
        
        # Take only a few samples for quick testing
        test_data = valid_data[:4]
        
        trainer = BARTTrainer()
        
        # Prepare data
        train_data, val_data = trainer.prepare_data(test_data, train_ratio=0.75)
        
        logger.info(f"Training data: {len(train_data)}, Validation data: {len(val_data)}")
        
        # Test training (very minimal)
        output_dir = "test_bart_model"
        
        metrics = trainer.train(
            train_data=train_data,
            val_data=val_data,
            output_dir=output_dir,
            epochs=1,  # Just 1 epoch for testing
            batch_size=1,
            max_length=512,  # Smaller for testing
            save_steps=10,
            eval_steps=10,
            logging_steps=5
        )
        
        logger.info(f"Training completed. Metrics: {metrics}")
        
        # Test inference
        if train_data:
            test_text = train_data[0]['text']
            summary = trainer.generate_summary(
                text=test_text,
                model_path=output_dir,
                max_length=128
            )
            
            logger.info(f"Original text length: {len(test_text)}")
            logger.info(f"Generated summary: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing BART trainer: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting pipeline test...")
    
    # Test 1: Dataset import
    success, data = test_multi_lexsum_import()
    if not success:
        logger.error("Dataset import test failed. Exiting.")
        return False
    
    # Test 2: Data processing
    success, processed_data = test_data_processing(data)
    if not success:
        logger.error("Data processing test failed. Exiting.")
        return False
    
    # Test 3: Model training (optional - requires GPU)
    try:
        import torch
        if torch.cuda.is_available():
            logger.info("GPU available - testing model training...")
            test_bart_trainer(processed_data)
        else:
            logger.info("No GPU available - skipping model training test")
    except ImportError:
        logger.info("PyTorch not available - skipping model training test")
    
    logger.info("Pipeline test completed successfully!")
    
    # Cleanup
    test_files = ["test_multi_lexsum.json", "test_bart_model"]
    for file in test_files:
        try:
            if os.path.exists(file):
                if os.path.isdir(file):
                    import shutil
                    shutil.rmtree(file)
                else:
                    os.remove(file)
        except Exception as e:
            logger.warning(f"Could not cleanup {file}: {e}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
