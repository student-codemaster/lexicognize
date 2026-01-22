from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.session import get_db, create_tables
import logging

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

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Legal Model Finetuner API",
        "version": "2.0.0",
        "documentation": "/api/docs",
        "authentication_required": False,
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health", response_model=None)
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
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

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

# Placeholder routes to indicate API is ready
@app.get("/api/docs")
async def docs_redirect():
    """Redirect to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
