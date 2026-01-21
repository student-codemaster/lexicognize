#!/usr/bin/env python3
"""
Validation script to check project structure and configuration
"""

import os
import sys
import json
from pathlib import Path

def check_project_structure():
    """Check if all required files and directories exist"""
    print("Checking project structure...")
    
    base_path = Path(__file__).parent
    backend_path = base_path / "backend"
    
    required_dirs = [
        "backend",
        "backend/app",
        "backend/app/models", 
        "backend/app/routes",
        "backend/app/utils",
        "backend/app/auth",
        "backend/app/database"
    ]
    
    required_files = [
        "backend/requirements.txt",
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/models/multi_model_trainer.py",
        "backend/app/models/bart_trainer.py",
        "backend/app/models/pegasus_trainer.py",
        "backend/app/models/multilingual_trainer.py",
        "backend/app/routes/training.py",
        "backend/app/routes/datasets.py",
        "backend/app/routes/inference.py",
        "backend/app/utils/huggingface_importer.py",
        "backend/app/utils/data_processor.py",
        "backend/app/utils/model_manager.py"
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"ERROR: Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"ERROR: Missing files: {missing_files}")
        return False
    
    print("SUCCESS: All required directories and files exist")
    return True

def check_multi_lexsum_integration():
    """Check if multi_lexsum dataset is properly integrated"""
    print("\nChecking multi_lexsum integration...")
    
    try:
        # Check the HuggingFace importer file
        importer_path = Path(__file__).parent / "backend/app/utils/huggingface_importer.py"
        
        with open(importer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for multi_lexsum in supported datasets
        if '"multi_lexsum"' not in content:
            print("ERROR: multi_lexsum not found in supported datasets")
            return False
        
        # Check for the correct path
        if '"allenai/multi_lexsum"' not in content:
            print("ERROR: multi_lexsum path not found")
            return False
        
        # Check for the name field
        if '"v20220616"' not in content:
            print("ERROR: multi_lexsum version name not found")
            return False
        
        # Check for formatting logic
        if 'summary/long' not in content:
            print("ERROR: multi_lexsum summary formatting not found")
            return False
        
        print("SUCCESS: multi_lexsum integration looks correct")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking multi_lexsum integration: {e}")
        return False

def check_model_trainers():
    """Check if model trainers are properly implemented"""
    print("\n🔍 Checking model trainers...")
    
    trainers = {
        "bart_trainer.py": "BARTTrainer",
        "pegasus_trainer.py": "PEGASUSTrainer", 
        "multi_model_trainer.py": "MultiModelTrainer",
        "multilingual_trainer.py": "MultilingualTrainer"
    }
    
    models_path = Path(__file__).parent / "backend/app/models"
    
    for filename, class_name in trainers.items():
        file_path = models_path / filename
        
        if not file_path.exists():
            print(f"❌ {filename} not found")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if f"class {class_name}" not in content:
                print(f"❌ {class_name} class not found in {filename}")
                return False
            
            if "def train" not in content:
                print(f"❌ train method not found in {filename}")
                return False
            
            if "def generate_summary" not in content:
                print(f"❌ generate_summary method not found in {filename}")
                return False
                
        except Exception as e:
            print(f"❌ Error checking {filename}: {e}")
            return False
    
    print("✅ All model trainers are properly implemented")
    return True

def check_utilities():
    """Check if utility files are properly implemented"""
    print("\n🔍 Checking utility files...")
    
    utils_path = Path(__file__).parent / "backend/app/utils"
    
    utilities = {
        "huggingface_importer.py": ["HuggingFaceDatasetImporter", "import_dataset", "_format_sample"],
        "data_processor.py": ["LegalDataProcessor", "process_dataset", "calculate_statistics"],
        "model_manager.py": ["ModelManager"],
        "evaluator.py": ["ModelEvaluator"]
    }
    
    for filename, required_elements in utilities.items():
        file_path = utils_path / filename
        
        if not file_path.exists():
            print(f"❌ {filename} not found")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for element in required_elements:
                if element not in content:
                    print(f"❌ {element} not found in {filename}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error checking {filename}: {e}")
            return False
    
    print("✅ All utility files are properly implemented")
    return True

def check_routes():
    """Check if API routes are properly implemented"""
    print("\n🔍 Checking API routes...")
    
    routes_path = Path(__file__).parent / "backend/app/routes"
    
    required_routes = {
        "training.py": ["start_training", "get_training_jobs"],
        "datasets.py": ["import_hf_dataset", "get_available_hf_datasets"],
        "inference.py": ["generate_summary", "batch_generate_summary", "evaluate_model"]
    }
    
    for filename, required_endpoints in required_routes.items():
        file_path = routes_path / filename
        
        if not file_path.exists():
            print(f"❌ {filename} not found")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for endpoint in required_endpoints:
                if endpoint not in content:
                    print(f"❌ {endpoint} not found in {filename}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error checking {filename}: {e}")
            return False
    
    print("✅ All API routes are properly implemented")
    return True

def check_requirements():
    """Check if requirements.txt contains necessary packages"""
    print("\n🔍 Checking requirements...")
    
    req_path = Path(__file__).parent / "backend/requirements.txt"
    
    if not req_path.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        required_packages = [
            "transformers",
            "datasets", 
            "torch",
            "fastapi",
            "sqlalchemy",
            "pydantic",
            "evaluate",
            "rouge-score",
            "nltk",
            "langdetect"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages in requirements: {missing_packages}")
            return False
        
        print("✅ All required packages are in requirements.txt")
        return True
        
    except Exception as e:
        print(f"❌ Error checking requirements: {e}")
        return False

def generate_summary_report():
    """Generate a summary report of the project"""
    print("\n📋 Generating project summary...")
    
    summary = {
        "project_name": "Lexicognize - AI Legal Text Summarization and Simplification",
        "description": "A comprehensive platform for fine-tuning and using AI models for legal text summarization and simplification",
        "key_features": [
            "Multi-model support (BART, PEGASUS, Multilingual)",
            "HuggingFace dataset integration (including multi_lexsum)",
            "User authentication and model management",
            "Training and evaluation pipelines",
            "RESTful API with FastAPI",
            "Data processing and validation",
            "Batch inference capabilities"
        ],
        "supported_datasets": [
            "multi_lexsum - Legal summarization with multiple summary lengths",
            "wikilarge - Wikipedia simplification",
            "xsum - Extreme summarization",
            "cnn_dailymail - News summarization",
            "samsum - Conversation summarization",
            "legal_bench - Legal NLP benchmark",
            "contract_nli - Contract analysis",
            "eurlex - Multi-lingual EU legislation"
        ],
        "model_types": [
            "BART - General purpose summarization",
            "PEGASUS - Abstractive summarization",
            "Multilingual - Multi-lingual support",
            "Multi-task - Combined summarization and simplification"
        ],
        "api_endpoints": {
            "training": "/api/training/*",
            "datasets": "/api/datasets/*", 
            "inference": "/api/inference/*",
            "evaluation": "/api/evaluation/*",
            "auth": "/api/auth/*"
        }
    }
    
    # Save summary to file
    summary_path = Path(__file__).parent / "project_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Summary report saved to {summary_path}")
    return True

def main():
    """Main validation function"""
    print("🚀 Starting Lexicognize Project Validation\n")
    
    checks = [
        check_project_structure,
        check_multi_lexsum_integration,
        check_model_trainers,
        check_utilities,
        check_routes,
        check_requirements,
        generate_summary_report
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                print(f"❌ Check failed: {check.__name__}")
        except Exception as e:
            print(f"❌ Error in {check.__name__}: {e}")
    
    print(f"\n📊 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All validation checks passed! The project is ready for use.")
        print("\n📝 Next Steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Set up database configuration in backend/app/config.py")
        print("3. Run the API server: uvicorn backend.app.main:app --reload")
        print("4. Access the API documentation: http://localhost:8000/api/docs")
        return True
    else:
        print("⚠️  Some validation checks failed. Please review and fix the issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
