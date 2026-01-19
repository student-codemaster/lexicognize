from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.security import get_current_user
from app.auth.schemas import UserInDB
from app.auth import crud as auth_crud
from app.models.multilingual_trainer import MultilingualTrainer
from app.services.email_service import EmailService

router = APIRouter()

class TrainingConfig(BaseModel):
    model_type: str  # "bart", "pegasus", "multilingual"
    dataset_id: int
    task: str  # "summarization", "simplification", "translation"
    name: Optional[str] = None
    description: Optional[str] = None
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 5e-5
    max_length: int = 1024
    target_max_length: int = 256
    languages: Optional[List[str]] = None

@router.post("/start")
async def start_training(
    config: TrainingConfig,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a training job."""
    # Check if dataset exists and belongs to user
    dataset = auth_crud.get_user_dataset(db, config.dataset_id, current_user.id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Create training job record
    job_id = str(uuid.uuid4())
    
    training_job = auth_crud.create_training_job(db, {
        'user_id': current_user.id,
        'job_id': job_id,
        'name': config.name or f"{config.model_type}_{config.task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'description': config.description,
        'model_type': config.model_type,
        'task': config.task,
        'dataset_id': config.dataset_id,
        'config': config.dict(exclude={'name', 'description', 'dataset_id'}),
        'status': 'pending'
    })
    
    # Start training in background
    background_tasks.add_task(
        run_training_task,
        job_id=job_id,
        user_id=current_user.id,
        config=config.dict(),
        dataset_path=dataset.file_path
    )
    
    return {
        "job_id": job_id,
        "message": "Training started",
        "training_job": training_job
    }

@router.get("/jobs")
async def get_training_jobs(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get training jobs for current user."""
    jobs = auth_crud.get_user_training_jobs(
        db, current_user.id, skip=skip, limit=limit, status=status
    )
    
    total = auth_crud.count_user_training_jobs(db, current_user.id, status=status)
    
    return {
        "jobs": jobs,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/jobs/{job_id}")
async def get_training_job(
    job_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific training job."""
    job = auth_crud.get_training_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return job

@router.delete("/jobs/{job_id}")
async def cancel_training_job(
    job_id: str,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a training job."""
    job = auth_crud.get_training_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    if job.status not in ['pending', 'running']:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Update job status
    job.status = 'cancelled'
    job.updated_at = datetime.utcnow()
    db.commit()
    
    # TODO: Actually stop the training process
    
    return {"message": "Training job cancelled"}

@router.get("/models")
async def get_user_models(
    skip: int = 0,
    limit: int = 50,
    model_type: Optional[str] = None,
    task: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trained models for current user."""
    models = auth_crud.get_user_models(
        db, current_user.id, skip=skip, limit=limit,
        model_type=model_type, task=task
    )
    
    total = auth_crud.count_user_models(db, current_user.id, model_type=model_type, task=task)
    
    return {
        "models": models,
        "total": total,
        "skip": skip,
        "limit": limit
    }

async def run_training_task(
    job_id: str,
    user_id: int,
    config: Dict[str, Any],
    dataset_path: str
):
    """Run training task in background."""
    from app.database.session import SessionLocal
    
    db = SessionLocal()
    try:
        # Update job status to running
        job = auth_crud.get_training_job_by_id(db, job_id)
        if job:
            job.status = 'running'
            job.started_at = datetime.utcnow()
            db.commit()
        
        # Load dataset
        with open(dataset_path, 'r') as f:
            dataset = json.load(f)
        
        # Initialize trainer based on model type
        if config['model_type'] == 'multilingual':
            trainer = MultilingualTrainer()
            languages = config.get('languages', ['en', 'hi', 'ta', 'kn'])
            
            # Prepare data
            train_data, val_data = trainer.prepare_multilingual_data(
                dataset,
                target_languages=languages
            )
            
            # Create output directory
            output_dir = f"data/models/{config['model_type']}_{config['task']}_{job_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Train model
            metrics = trainer.train(
                train_data=train_data,
                val_data=val_data,
                output_dir=output_dir,
                languages=languages,
                epochs=config.get('epochs', 3),
                batch_size=config.get('batch_size', 4),
                learning_rate=config.get('learning_rate', 5e-5),
                max_length=config.get('max_length', 1024),
                target_max_length=config.get('target_max_length', 256)
            )
            
        else:
            # For BART or PEGASUS
            from app.models.multi_model_trainer import MultiModelTrainer
            
            trainer = MultiModelTrainer(
                model_type=config['model_type'],
                task=config['task']
            )
            
            # Prepare data
            train_data, val_data = trainer.prepare_data(dataset)
            
            # Create output directory
            output_dir = f"data/models/{config['model_type']}_{config['task']}_{job_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Train model
            metrics = trainer.train(
                train_data=train_data,
                val_data=val_data,
                output_dir=output_dir,
                epochs=config.get('epochs', 3),
                batch_size=config.get('batch_size', 4),
                learning_rate=config.get('learning_rate', 5e-5),
                max_length=config.get('max_length', 1024),
                target_max_length=config.get('target_max_length', 256)
            )
        
        # Update job status and save model
        job = auth_crud.get_training_job_by_id(db, job_id)
        if job:
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            job.metrics = metrics
            job.model_path = output_dir
            job.progress = 100
            db.commit()
            
            # Create user model record
            auth_crud.create_user_model(db, {
                'user_id': user_id,
                'name': job.name,
                'description': job.description,
                'model_type': config['model_type'],
                'task': config['task'],
                'model_path': output_dir,
                'training_job_id': job.id,
                'dataset_id': job.dataset_id,
                'metadata': {
                    'epochs': config.get('epochs', 3),
                    'batch_size': config.get('batch_size', 4),
                    'learning_rate': config.get('learning_rate', 5e-5),
                    'metrics': metrics
                }
            })
            
            # Send notification email
            user = auth_crud.get_user_by_id(db, user_id)
            if user and user.email:
                email_service = EmailService()
                email_service.send_notification_email(
                    to_email=user.email,
                    username=user.username,
                    notification_type='training_completed',
                    data={
                        'job_id': job_id,
                        'model_name': job.name,
                        'metrics': metrics
                    }
                )
        
    except Exception as e:
        # Update job status to failed
        job = auth_crud.get_training_job_by_id(db, job_id)
        if job:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.commit()
            
            # Send failure notification
            user = auth_crud.get_user_by_id(db, user_id)
            if user and user.email:
                email_service = EmailService()
                email_service.send_notification_email(
                    to_email=user.email,
                    username=user.username,
                    notification_type='training_failed',
                    data={
                        'job_id': job_id,
                        'error': str(e)
                    }
                )
        
        raise e
    
    finally:
        db.close()