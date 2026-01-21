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
        importer_path = Path(__file__).parent / "backend/app/utils/huggingface_importer.py"
        
        with open(importer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('"multi_lexsum"', 'multi_lexsum not found in supported datasets'),
            ('"allenai/multi_lexsum"', 'multi_lexsum path not found'),
            ('"v20220616"', 'multi_lexsum version name not found'),
            ('summary/long', 'multi_lexsum summary formatting not found')
        ]
        
        for check, error_msg in checks:
            if check not in content:
                print(f"ERROR: {error_msg}")
                return False
        
        print("SUCCESS: multi_lexsum integration looks correct")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking multi_lexsum integration: {e}")
        return False

def check_model_trainers():
    """Check if model trainers are properly implemented"""
    print("\nChecking model trainers...")
    
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
            print(f"ERROR: {filename} not found")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = [
                (f"class {class_name}", f"{class_name} class not found in {filename}"),
                ("def train", f"train method not found in {filename}"),
                ("def generate_summary", f"generate_summary method not found in {filename}")
            ]
            
            for check, error_msg in checks:
                if check not in content:
                    print(f"ERROR: {error_msg}")
                    return False
                
        except Exception as e:
            print(f"ERROR: Error checking {filename}: {e}")
            return False
    
    print("SUCCESS: All model trainers are properly implemented")
    return True

def check_utilities():
    """Check if utility files are properly implemented"""
    print("\nChecking utility files...")
    
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
            print(f"ERROR: {filename} not found")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for element in required_elements:
                if element not in content:
                    print(f"ERROR: {element} not found in {filename}")
                    return False
                    
        except Exception as e:
            print(f"ERROR: Error checking {filename}: {e}")
            return False
    
    print("SUCCESS: All utility files are properly implemented")
    return True

def check_routes():
    """Check if API routes are properly implemented"""
    print("\nChecking API routes...")
    
    routes_path = Path(__file__).parent / "backend/app/routes"
    
    required_routes = {
        "training.py": ["start_training", "get_training_jobs"],
        "datasets.py": ["import_hf_dataset", "get_available_hf_datasets"],
        "inference.py": ["generate_summary", "batch_generate_summary", "evaluate_model"]
    }
    
    for filename, required_endpoints in required_routes.items():
        file_path = routes_path / filename
        
        if not file_path.exists():
            print(f"ERROR: {filename} not found")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for endpoint in required_endpoints:
                if endpoint not in content:
                    print(f"ERROR: {endpoint} not found in {filename}")
                    return False
                    
        except Exception as e:
            print(f"ERROR: Error checking {filename}: {e}")
            return False
    
    print("SUCCESS: All API routes are properly implemented")
    return True

def check_requirements():
    """Check if requirements.txt contains necessary packages"""
    print("\nChecking requirements...")
    
    req_path = Path(__file__).parent / "backend/requirements.txt"
    
    if not req_path.exists():
        print("ERROR: requirements.txt not found")
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
            print(f"ERROR: Missing packages in requirements: {missing_packages}")
            return False
        
        print("SUCCESS: All required packages are in requirements.txt")
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking requirements: {e}")
        return False

def main():
    """Main validation function"""
    print("Starting Lexicognize Project Validation\n")
    
    checks = [
        check_project_structure,
        check_multi_lexsum_integration,
        check_model_trainers,
        check_utilities,
        check_routes,
        check_requirements
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
            else:
                print(f"ERROR: Check failed: {check.__name__}")
        except Exception as e:
            print(f"ERROR: Error in {check.__name__}: {e}")
    
    print(f"\nValidation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("SUCCESS: All validation checks passed! The project is ready for use.")
        print("\nNext Steps:")
        print("1. Install dependencies: pip install -r backend/requirements.txt")
        print("2. Set up database configuration in backend/app/config.py")
        print("3. Run the API server: uvicorn backend.app.main:app --reload")
        print("4. Access the API documentation: http://localhost:8000/api/docs")
        return True
    else:
        print("WARNING: Some validation checks failed. Please review and fix the issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
