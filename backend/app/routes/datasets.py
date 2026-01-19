from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
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

router = APIRouter()

@router.post("/upload")
async def upload_dataset(
    files: List[UploadFile] = File(...),
    merge: bool = False,
    dataset_name: Optional[str] = None,
    description: Optional[str] = None,
    is_public: bool = False,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload dataset files."""
    uploaded_files = []
    all_data = []
    
    for file in files:
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} must be a JSON file"
            )
        
        # Read file content
        content = await file.read()
        
        try:
            data = json.loads(content)
            
            # Validate structure
            if not LegalDataProcessor.validate_legal_json(data):
                raise ValueError(f"Invalid structure in {file.filename}")
            
            # Add to collection
            if isinstance(data, list):
                all_data.extend(data)
            else:
                all_data.append(data)
            
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "valid": True,
                "samples": len(data) if isinstance(data, list) else 1
            })
            
        except Exception as e:
            uploaded_files.append({
                "filename": file.filename,
                "size": len(content),
                "valid": False,
                "error": str(e)
            })
    
    if not all_data:
        raise HTTPException(
            status_code=400,
            detail="No valid data found in uploaded files"
        )
    
    # Generate dataset name if not provided
    if not dataset_name:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dataset_name = f"dataset_{timestamp}"
    
    # Create dataset hash
    dataset_hash = hashlib.md5(
        json.dumps(all_data, sort_keys=True).encode()
    ).hexdigest()
    
    # Save dataset file
    datasets_dir = f"data/uploads/{current_user.id}"
    os.makedirs(datasets_dir, exist_ok=True)
    
    file_path = os.path.join(datasets_dir, f"{dataset_name}.json")
    
    with open(file_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    # Calculate statistics
    statistics = LegalDataProcessor.calculate_statistics(all_data)
    
    # Create dataset record
    dataset = auth_crud.create_user_dataset(db, {
        'user_id': current_user.id,
        'name': dataset_name,
        'description': description,
        'file_path': file_path,
        'file_size': os.path.getsize(file_path),
        'file_format': 'json',
        'original_filename': ', '.join([f["filename"] for f in uploaded_files if f.get("valid", False)]),
        'metadata': {
            'samples': len(all_data),
            'languages': statistics.get('languages', ['en']),
            'categories': statistics.get('categories', []),
            'created_from': 'upload',
            'source_files': [f["filename"] for f in uploaded_files if f.get("valid", False)]
        },
        'statistics': statistics,
        'is_public': is_public
    })
    
    return {
        "dataset": dataset,
        "uploaded_files": uploaded_files,
        "total_samples": len(all_data),
        "statistics": statistics
    }

@router.get("/")
async def list_datasets(
    skip: int = 0,
    limit: int = 50,
    is_public: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List datasets for current user."""
    datasets = auth_crud.get_user_datasets(
        db, current_user.id, skip=skip, limit=limit,
        is_public=is_public, search=search
    )
    
    total = auth_crud.count_user_datasets(
        db, current_user.id, is_public=is_public, search=search
    )
    
    return {
        "datasets": datasets,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/public")
async def list_public_datasets(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List public datasets."""
    datasets = auth_crud.get_public_datasets(
        db, skip=skip, limit=limit, search=search
    )
    
    total = auth_crud.count_public_datasets(db, search=search)
    
    return {
        "datasets": datasets,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dataset details."""
    dataset = auth_crud.get_user_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load dataset content
    with open(dataset.file_path, 'r') as f:
        content = json.load(f)
    
    return {
        "dataset": dataset,
        "content_preview": content[:10] if isinstance(content, list) and len(content) > 10 else content,
        "total_samples": len(content) if isinstance(content, list) else 1
    }

@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a dataset."""
    dataset = auth_crud.get_user_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Delete file
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    
    # Delete record
    auth_crud.delete_user_dataset(db, dataset_id, current_user.id)
    
    return {"message": "Dataset deleted successfully"}

@router.post("/{dataset_id}/share")
async def share_dataset(
    dataset_id: int,
    user_ids: List[int],
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share dataset with other users."""
    dataset = auth_crud.get_user_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Update shared_with
    dataset.is_shared = True
    dataset.shared_with = user_ids
    db.commit()
    
    return {"message": "Dataset shared successfully"}

@router.get("/{dataset_id}/stats")
async def get_dataset_stats(
    dataset_id: int,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dataset statistics."""
    dataset = auth_crud.get_user_dataset(db, dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Load dataset
    with open(dataset.file_path, 'r') as f:
        data = json.load(f)
    
    # Calculate statistics
    statistics = LegalDataProcessor.calculate_statistics(data)
    
    return {
        "dataset_id": dataset_id,
        "dataset_name": dataset.name,
        "statistics": statistics
    }