#!/usr/bin/env python3
"""
Code structure test for summarization, simplification, and multilingual output functionality
"""

import sys
import os
from pathlib import Path

def check_summarization_methods():
    """Check if summarization methods exist in code"""
    print("Checking Summarization Methods...")
    
    try:
        # Check BART trainer
        bart_file = Path(__file__).parent / "backend/app/models/bart_trainer.py"
        if bart_file.exists():
            with open(bart_file, 'r') as f:
                bart_content = f.read()
            
            if "def generate_summary" in bart_content:
                print("SUCCESS: BART trainer has generate_summary method")
            else:
                print("ERROR: BART trainer missing generate_summary method")
                return False
        else:
            print("ERROR: BART trainer file not found")
            return False
        
        # Check MultiModelTrainer
        multi_file = Path(__file__).parent / "backend/app/models/multi_model_trainer.py"
        if multi_file.exists():
            with open(multi_file, 'r') as f:
                multi_content = f.read()
            
            if "def generate_summary" in multi_content:
                print("SUCCESS: MultiModelTrainer has generate_summary method")
            else:
                print("ERROR: MultiModelTrainer missing generate_summary method")
                return False
        else:
            print("ERROR: MultiModelTrainer file not found")
            return False
            
        print("SUCCESS: Summarization methods verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking summarization: {e}")
        return False

def check_simplification_methods():
    """Check if simplification methods exist in code"""
    print("\nChecking Simplification Methods...")
    
    try:
        # Check MultiModelTrainer for simplification support
        multi_file = Path(__file__).parent / "backend/app/models/multi_model_trainer.py"
        if multi_file.exists():
            with open(multi_file, 'r') as f:
                multi_content = f.read()
            
            # Check for simplification task handling
            if 'task="simplification"' in multi_content or '"simplification"' in multi_content:
                print("SUCCESS: MultiModelTrainer supports simplification task")
            else:
                print("ERROR: MultiModelTrainer doesn't support simplification")
                return False
        else:
            print("ERROR: MultiModelTrainer file not found")
            return False
        
        # Check dataset support for simplification
        importer_file = Path(__file__).parent / "backend/app/utils/huggingface_importer.py"
        if importer_file.exists():
            with open(importer_file, 'r') as f:
                importer_content = f.read()
            
            if '"wikilarge"' in importer_content and '"simplification"' in importer_content:
                print("SUCCESS: Wikilarge simplification dataset supported")
            else:
                print("ERROR: Wikilarge simplification dataset not properly configured")
                return False
        else:
            print("ERROR: HuggingFace importer file not found")
            return False
            
        print("SUCCESS: Simplification methods verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking simplification: {e}")
        return False

def check_multilingual_methods():
    """Check if multilingual methods exist in code"""
    print("\nChecking Multilingual Methods...")
    
    try:
        # Check MultilingualTrainer
        multilingual_file = Path(__file__).parent / "backend/app/models/multilingual_trainer.py"
        if multilingual_file.exists():
            with open(multilingual_file, 'r') as f:
                multilingual_content = f.read()
            
            required_methods = ['def train', 'def evaluate', 'def generate_summary', 'def translate_text']
            missing_methods = []
            
            for method in required_methods:
                if method not in multilingual_content:
                    missing_methods.append(method)
            
            if missing_methods:
                print(f"ERROR: MultilingualTrainer missing methods: {missing_methods}")
                return False
            else:
                print("SUCCESS: MultilingualTrainer has all required methods")
        else:
            print("ERROR: MultilingualTrainer file not found")
            return False
        
        # Check multilingual dataset support
        importer_file = Path(__file__).parent / "backend/app/utils/huggingface_importer.py"
        if importer_file.exists():
            with open(importer_file, 'r') as f:
                importer_content = f.read()
            
            if '"eurlex"' in importer_content:
                # Check if it supports multiple languages
                if '"en"' in importer_content and '"de"' in importer_content:
                    print("SUCCESS: Multilingual dataset support found")
                else:
                    print("ERROR: Multilingual dataset doesn't support multiple languages")
                    return False
            else:
                print("ERROR: No multilingual dataset support found")
                return False
        else:
            print("ERROR: HuggingFace importer file not found")
            return False
            
        print("SUCCESS: Multilingual methods verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking multilingual: {e}")
        return False

def check_multi_lexsum_output():
    """Check multi_lexsum specific output functionality"""
    print("\nChecking Multi-Lexsum Output...")
    
    try:
        importer_file = Path(__file__).parent / "backend/app/utils/huggingface_importer.py"
        if not importer_file.exists():
            print("ERROR: HuggingFace importer file not found")
            return False
        
        with open(importer_file, 'r') as f:
            importer_content = f.read()
        
        # Check multi_lexsum configuration
        if '"multi_lexsum"' not in importer_content:
            print("ERROR: Multi-lexsum dataset not supported")
            return False
        
        # Check for required fields
        required_fields = ["summary/long", "summary/short", "summary/tiny"]
        missing_fields = []
        
        for field in required_fields:
            if f'"{field}"' not in importer_content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"ERROR: Multi-lexsum missing fields: {missing_fields}")
            return False
        else:
            print("SUCCESS: Multi-lexsum has all required summary fields")
        
        # Check version name
        if '"v20220616"' not in importer_content:
            print("ERROR: Multi-lexsum version not correctly set")
            return False
        else:
            print("SUCCESS: Multi-lexsum version correctly set")
        
        # Check formatting logic
        if 'summary_long' in importer_content and 'summary_short' in importer_content and 'summary_tiny' in importer_content:
            print("SUCCESS: Multi-lexsum formatting logic found")
        else:
            print("ERROR: Multi-lexsum formatting logic missing")
            return False
            
        print("SUCCESS: Multi-lexsum functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking multi-lexsum: {e}")
        return False

def check_inference_api():
    """Check inference API output functionality"""
    print("\nChecking Inference API...")
    
    try:
        inference_file = Path(__file__).parent / "backend/app/routes/inference.py"
        if not inference_file.exists():
            print("ERROR: Inference API file not found")
            return False
        
        with open(inference_file, 'r') as f:
            inference_content = f.read()
        
        # Check for required endpoints
        required_endpoints = ["generate_summary", "batch_generate_summary", "evaluate_model"]
        missing_endpoints = []
        
        for endpoint in required_endpoints:
            if endpoint not in inference_content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"ERROR: Inference API missing endpoints: {missing_endpoints}")
            return False
        else:
            print("SUCCESS: Inference API has all required endpoints")
        
        # Check for request/response models
        if "InferenceRequest" in inference_content and "InferenceResponse" in inference_content:
            print("SUCCESS: Inference API has proper request/response models")
        else:
            print("ERROR: Inference API missing request/response models")
            return False
            
        print("SUCCESS: Inference API functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking inference API: {e}")
        return False

def check_output_formatting():
    """Check output formatting functionality"""
    print("\nChecking Output Formatting...")
    
    try:
        # Check data processor
        processor_file = Path(__file__).parent / "backend/app/utils/data_processor.py"
        if processor_file.exists():
            with open(processor_file, 'r') as f:
                processor_content = f.read()
            
            if "def process_dataset" in processor_content and "def calculate_statistics" in processor_content:
                print("SUCCESS: Data processor has output formatting methods")
            else:
                print("ERROR: Data processor missing output formatting methods")
                return False
        else:
            print("ERROR: Data processor file not found")
            return False
        
        # Check evaluator
        evaluator_file = Path(__file__).parent / "backend/app/utils/evaluator.py"
        if evaluator_file.exists():
            with open(evaluator_file, 'r') as f:
                evaluator_content = f.read()
            
            if "class ModelEvaluator" in evaluator_content:
                print("SUCCESS: Model evaluator available for output assessment")
            else:
                print("ERROR: Model evaluator not found")
                return False
        else:
            print("ERROR: Evaluator file not found")
            return False
            
        print("SUCCESS: Output formatting functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking output formatting: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Lexicognize Output Functionality (Code Structure)\n")
    
    tests = [
        check_summarization_methods,
        check_simplification_methods,
        check_multilingual_methods,
        check_multi_lexsum_output,
        check_inference_api,
        check_output_formatting
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"ERROR: Test error: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All output functionality code structure verified!")
        print("\nSTATUS CHECK:")
        print("Summarization: CODE STRUCTURE OK")
        print("Simplification: CODE STRUCTURE OK") 
        print("Multilingual: CODE STRUCTURE OK")
        print("Multi-lexsum: CODE STRUCTURE OK")
        print("Inference API: CODE STRUCTURE OK")
        print("Output Formatting: CODE STRUCTURE OK")
        print("\nNOTE: Runtime functionality requires dependency installation:")
        print("pip install -r backend/requirements.txt")
        return True
    else:
        print("WARNING: Some code structure tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
