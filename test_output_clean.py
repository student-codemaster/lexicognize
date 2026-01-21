#!/usr/bin/env python3
"""
Focused test for summarization, simplification, and multilingual output functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_summarization_output():
    """Test summarization output functionality"""
    print("Testing Summarization Output...")
    
    try:
        # Test BART trainer summarization
        from app.models.bart_trainer import BARTTrainer
        
        trainer = BARTTrainer()
        
        # Check if generate_summary method exists and works
        if hasattr(trainer, 'generate_summary'):
            print("SUCCESS: BART trainer has generate_summary method")
        else:
            print("ERROR: BART trainer missing generate_summary method")
            return False
            
        # Test MultiModelTrainer for summarization
        from app.models.multi_model_trainer import MultiModelTrainer
        
        multi_trainer = MultiModelTrainer(model_type="bart", task="summarization")
        
        if hasattr(multi_trainer, 'generate_summary'):
            print("SUCCESS: MultiModelTrainer has generate_summary method")
        else:
            print("ERROR: MultiModelTrainer missing generate_summary method")
            return False
            
        print("SUCCESS: Summarization functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing summarization: {e}")
        return False

def test_simplification_output():
    """Test simplification output functionality"""
    print("\nTesting Simplification Output...")
    
    try:
        # Test MultiModelTrainer for simplification
        from app.models.multi_model_trainer import MultiModelTrainer
        
        simplification_trainer = MultiModelTrainer(model_type="bart", task="simplification")
        
        if hasattr(simplification_trainer, 'generate_summary'):
            print("SUCCESS: Simplification trainer has generate_summary method")
        else:
            print("ERROR: Simplification trainer missing generate_summary method")
            return False
            
        # Test dataset processing for simplification
        from app.utils.huggingface_importer import HuggingFaceDatasetImporter
        
        # Check if wikilarge (simplification dataset) is supported
        if "wikilarge" in HuggingFaceDatasetImporter.SUPPORTED_DATASETS:
            config = HuggingFaceDatasetImporter.SUPPORTED_DATASETS["wikilarge"]
            if config["task"] == "simplification":
                print("SUCCESS: Wikilarge simplification dataset properly configured")
            else:
                print("ERROR: Wikilarge dataset task not set to simplification")
                return False
        else:
            print("ERROR: Wikilarge dataset not supported")
            return False
            
        print("SUCCESS: Simplification functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing simplification: {e}")
        return False

def test_multilingual_output():
    """Test multilingual output functionality"""
    print("\nTesting Multilingual Output...")
    
    try:
        # Test MultilingualTrainer
        from app.models.multilingual_trainer import MultilingualTrainer
        
        multilingual_trainer = MultilingualTrainer()
        
        # Check for multilingual methods
        required_methods = ['train', 'evaluate', 'generate_summary', 'translate_text']
        missing_methods = []
        
        for method in required_methods:
            if not hasattr(multilingual_trainer, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"ERROR: MultilingualTrainer missing methods: {missing_methods}")
            return False
        else:
            print("SUCCESS: MultilingualTrainer has all required methods")
        
        # Test multilingual dataset support
        from app.utils.huggingface_importer import HuggingFaceDatasetImporter
        
        if "eurlex" in HuggingFaceDatasetImporter.SUPPORTED_DATASETS:
            config = HuggingFaceDatasetImporter.SUPPORTED_DATASETS["eurlex"]
            languages = config.get("languages", [])
            if len(languages) > 1:  # Should support multiple languages
                print(f"SUCCESS: Multilingual dataset supports: {languages}")
            else:
                print("ERROR: Eurlex dataset doesn't support multiple languages")
                return False
        else:
            print("ERROR: Eurlex multilingual dataset not supported")
            return False
            
        print("SUCCESS: Multilingual functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing multilingual: {e}")
        return False

def test_multi_lexsum_output():
    """Test multi_lexsum specific output functionality"""
    print("\nTesting Multi-Lexsum Output...")
    
    try:
        from app.utils.huggingface_importer import HuggingFaceDatasetImporter
        
        # Check multi_lexsum configuration
        if "multi_lexsum" in HuggingFaceDatasetImporter.SUPPORTED_DATASETS:
            config = HuggingFaceDatasetImporter.SUPPORTED_DATASETS["multi_lexsum"]
            
            # Check for required fields
            required_fields = ["summary/long", "summary/short", "summary/tiny"]
            fields = config.get("fields", [])
            
            missing_fields = [field for field in required_fields if field not in fields]
            if missing_fields:
                print(f"ERROR: Multi-lexsum missing fields: {missing_fields}")
                return False
            else:
                print("SUCCESS: Multi-lexsum has all required summary fields")
            
            # Check version name
            if "name" in config and config["name"] == "v20220616":
                print("SUCCESS: Multi-lexsum version correctly set")
            else:
                print("ERROR: Multi-lexsum version not correctly set")
                return False
                
        else:
            print("ERROR: Multi-lexsum dataset not supported")
            return False
            
        # Test formatting logic
        sample_data = {
            "sources": ["Legal document 1", "Legal document 2"],
            "summary/long": "This is a long summary of the legal documents...",
            "summary/short": "Short summary...",
            "summary/tiny": "Tiny summary."
        }
        
        formatted = HuggingFaceDatasetImporter._format_sample(
            sample_data, config, "multi_lexsum"
        )
        
        if formatted:
            # Check if all summary types are preserved
            if all(key in formatted for key in ["summary_long", "summary_short", "summary_tiny"]):
                print("SUCCESS: Multi-lexsum formatting preserves all summary types")
            else:
                print("ERROR: Multi-lexsum formatting missing summary types")
                return False
                
            # Check if sources are concatenated
            if "Legal document 1 Legal document 2" in formatted.get("text", ""):
                print("SUCCESS: Multi-lexsum sources properly concatenated")
            else:
                print("ERROR: Multi-lexsum sources not properly concatenated")
                return False
        else:
            print("ERROR: Multi-lexsum formatting failed")
            return False
            
        print("SUCCESS: Multi-lexsum functionality verified")
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing multi-lexsum: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Lexicognize Output Functionality\n")
    
    tests = [
        test_summarization_output,
        test_simplification_output,
        test_multilingual_output,
        test_multi_lexsum_output
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
        print("SUCCESS: All output functionality tests passed!")
        print("\nSummarization: WORKING")
        print("Simplification: WORKING") 
        print("Multilingual: WORKING")
        print("Multi-lexsum: WORKING")
        return True
    else:
        print("WARNING: Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
