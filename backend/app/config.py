import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Legal Model Finetuner"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:password@localhost/legal_models"
    )
    DATABASE_TEST_URL: Optional[str] = os.getenv("DATABASE_TEST_URL")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password hashing
    HASHING_ALGORITHM: str = "bcrypt"
    
    # Email (for password reset)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Storage paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    UPLOADS_DIR: str = os.path.join(DATA_DIR, "uploads")
    MODELS_DIR: str = os.path.join(DATA_DIR, "models")
    DATASETS_DIR: str = os.path.join(DATA_DIR, "datasets")
    
    # Model defaults
    DEFAULT_MODEL_TYPE: str = "bart"
    DEFAULT_EPOCHS: int = 3
    DEFAULT_BATCH_SIZE: int = 4
    DEFAULT_LEARNING_RATE: float = 5e-5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()