from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import json
import os
import shutil
import hashlib
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.security import get_current_user
from app.auth.schemas import UserInDB
from app.auth import crud as auth_crud
from app.utils.data_processor import LegalDataProcessor
from app.utils.huggingface_importer import HuggingFaceDatasetImporter

router = APIRouter()

# ... (existing upload, list, delete endpoints remain the same) ...

@router.get("/huggingface/available")
async def get_available_hf_datasets(
    task: Optional[str] = None,
    search: Optional[str] = None
):
    """Get available datasets from Hugging Face Hub"""
    try:
        if search:
            datasets = HuggingFaceDatasetImporter.search_datasets(search, task)
        else:
            datasets = HuggingFaceDatasetImporter.get_available_datasets()
        
        return {
            "datasets": datasets,
            "total": len(datasets),
            "task": task,
            "search": search
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching datasets: {str(e)}"
        )

@router.get("/huggingface/{dataset_id}/info")
async def get_hf_dataset_info(dataset_id: str):
    """Get information about a Hugging Face dataset"""
    try:
        info = HuggingFaceDatasetImporter.get_dataset_info(dataset_id)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dataset info: {str(e)}"
        )

@router.post("/huggingface/import")
async def import_hf_dataset(
    dataset_id: str,
    split: str = "train",
    sample_size: Optional[int] = None,
    dataset_name: Optional[str] = None,
    description: Optional[str] = None,
    is_public: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import dataset from Hugging Face Hub"""
    # Check if dataset is supported
    if dataset_id not in HuggingFaceDatasetImporter.SUPPORTED_DATASETS:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset_id} not supported"
        )
    
    # Generate dataset name if not provided
    if not dataset_name:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = f"{dataset_id}_{split}_{timestamp}"
    
    # Create dataset directory
    datasets_dir = f"data/uploads/{current_user.id}"
    os.makedirs(datasets_dir, exist_ok=True)
    
    file_path = os.path.join(datasets_dir, f"{dataset_name}.json")
    
    # Import dataset in background
    background_tasks.add_task(
        import_hf_dataset_background,
        dataset_id=dataset_id,
        split=split,
        sample_size=sample_size,
        file_path=file_path,
        dataset_name=dataset_name,
        description=description,
        is_public=is_public,
        user_id=current_user.id,
        db=db
    )
    
    return {
        "message": "Dataset import started in background",
        "dataset_id": dataset_id,
        "dataset_name": dataset_name,
        "file_path": file_path
    }

@router.get("/huggingface/import/status/{import_id}")
async def get_import_status(import_id: str):
    """Get status of a dataset import job"""
    # This would track ongoing imports
    # For simplicity, we'll return a mock response
    return {
        "import_id": import_id,
        "status": "completed",  # or "processing", "failed"
        "progress": 100,
        "message": "Import completed successfully"
    }

async def import_hf_dataset_background(
    dataset_id: str,
    split: str,
    sample_size: Optional[int],
    file_path: str,
    dataset_name: str,
    description: Optional[str],
    is_public: bool,
    user_id: int,
    db: Session
):
    """Background task to import dataset from Hugging Face"""
    from app.database.session import SessionLocal
    
    db = SessionLocal()
    try:
        # Import dataset
        result = HuggingFaceDatasetImporter.import_dataset(
            dataset_id=dataset_id,
            split=split,
            sample_size=sample_size,
            save_path=file_path
        )
        
        if result["status"] != "success":
            raise Exception(f"Import failed: {result.get('error', 'Unknown error')}")
        
        # Load imported data to calculate statistics
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        statistics = LegalDataProcessor.calculate_statistics(data)
        
        # Create dataset record
        dataset = auth_crud.create_user_dataset(db, {
            'user_id': user_id,
            'name': dataset_name,
            'description': description or f"Imported from Hugging Face: {dataset_id}",
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'file_format': 'json',
            'original_filename': f"hf_{dataset_id}_{split}.json",
            'metadata': {
                'samples': len(data),
                'languages': statistics.get('languages', ['en']),
                'categories': statistics.get('categories', []),
                'created_from': 'huggingface',
                'source_dataset': dataset_id,
                'split': split,
                'sample_size': sample_size
            },
            'statistics': statistics,
            'is_public': is_public
        })
        
        logger.info(f"Successfully imported dataset {dataset_id} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error importing dataset in background: {e}")
        
        # Clean up file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Could store failure status in database
        
    finally:
        db.close()