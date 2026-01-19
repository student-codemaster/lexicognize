from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from app.database.session import get_db, create_tables
from app.auth.routes import router as auth_router
from app.auth.security import get_current_user
from app.auth.schemas import UserInDB

# Import other routers
from app.routes import (
    training, evaluation, inference, pdf_processor, 
    datasets, translation, transliteration, multilingual
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Legal Model Finetuner API",
    description="API for fine-tuning legal text models with authentication",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Include routers with authentication
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# Protected routers (require authentication)
app.include_router(datasets.router, prefix="/api/datasets", tags=["datasets"], dependencies=[Depends(get_current_user)])
app.include_router(training.router, prefix="/api/training", tags=["training"], dependencies=[Depends(get_current_user)])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"], dependencies=[Depends(get_current_user)])
app.include_router(inference.router, prefix="/api/inference", tags=["inference"], dependencies=[Depends(get_current_user)])
app.include_router(pdf_processor.router, prefix="/api/pdf", tags=["pdf"], dependencies=[Depends(get_current_user)])
app.include_router(translation.router, prefix="/api/translation", tags=["translation"], dependencies=[Depends(get_current_user)])
app.include_router(transliteration.router, prefix="/api/transliteration", tags=["transliteration"], dependencies=[Depends(get_current_user)])
app.include_router(multilingual.router, prefix="/api/multilingual", tags=["multilingual"], dependencies=[Depends(get_current_user)])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Legal Model Finetuner API")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Create data directories
    import os
    directories = [
        "data/uploads",
        "data/models",
        "data/datasets",
        "data/processed_pdfs",
        "data/training_logs",
        "data/exports"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("Application startup completed")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Legal Model Finetuner API",
        "version": "2.0.0",
        "documentation": "/api/docs",
        "authentication_required": True,
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity test."""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "ok",
                "authentication": "enabled",
                "model_training": "ready"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

# User profile endpoint
@app.get("/api/profile")
async def get_profile(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with statistics."""
    from app.auth import crud
    
    user_stats = crud.get_user_stats(db, current_user.id)
    
    return {
        "user": current_user,
        "stats": user_stats,
        "permissions": {
            "can_train_models": current_user.role in ["admin", "researcher", "user"],
            "can_upload_datasets": True,
            "can_access_api": True,
            "can_manage_users": current_user.role == "admin"
        }
    }

# System information endpoint
@app.get("/api/system/info")
async def system_info(current_user: UserInDB = Depends(get_current_user)):
    """Get system information (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    import psutil
    import platform
    from app.config import settings
    
    return {
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "application": {
            "version": settings.APP_VERSION,
            "debug": settings.DEBUG,
            "data_directory": settings.DATA_DIR
        },
        "database": {
            "url": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else "hidden"
        }
    }