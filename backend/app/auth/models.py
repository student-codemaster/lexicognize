from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, 
    Text, ForeignKey, Enum, JSON, LargeBinary, Float
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database.session import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    RESEARCHER = "researcher"
    LEGAL_PROFESSIONAL = "legal_professional"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    avatar_url = Column(String(500))
    bio = Column(Text)
    organization = Column(String(255))
    position = Column(String(255))
    
    # Preferences
    preferences = Column(JSON, default=lambda: {
        "language": "en",
        "theme": "light",
        "notifications": True,
        "default_model": "bart"
    })
    
    # Contact information
    phone_number = Column(String(50))
    address = Column(Text)
    country = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    email_verified_at = Column(DateTime(timezone=True))
    
    # Relationships
    training_jobs = relationship("TrainingJob", back_populates="user")
    datasets = relationship("UserDataset", back_populates="user")
    models = relationship("UserModel", back_populates="user")
    api_keys = relationship("ApiKey", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    key = Column(String(100), unique=True, nullable=False)
    secret = Column(String(255), nullable=False)
    scopes = Column(JSON, default=lambda: ["read", "write"])
    rate_limit = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, name={self.name}, user_id={self.user_id})>"

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id})>"

# Additional models for the application

class TrainingJob(Base):
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255))
    description = Column(Text)
    
    # Configuration
    model_type = Column(String(50), nullable=False)  # bart, pegasus, multilingual
    task = Column(String(50), nullable=False)  # summarization, simplification, translation
    dataset_id = Column(Integer, ForeignKey("user_datasets.id"))
    
    # Hyperparameters
    config = Column(JSON, default=lambda: {
        "epochs": 3,
        "batch_size": 4,
        "learning_rate": 5e-5,
        "max_length": 1024,
        "target_max_length": 256
    })
    
    # Status
    status = Column(String(50), default="pending")  # pending, running, completed, failed, cancelled
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text)
    
    # Results
    metrics = Column(JSON)
    model_path = Column(String(500))
    logs = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="training_jobs")
    dataset = relationship("UserDataset")
    
    def __repr__(self):
        return f"<TrainingJob(id={self.id}, name={self.name}, status={self.status})>"

class UserDataset(Base):
    __tablename__ = "user_datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # File information
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_format = Column(String(50))  # json, csv, txt
    original_filename = Column(String(255))
    
    # Dataset metadata
    metadata_info = Column(JSON, default=lambda: {
        "samples": 0,
        "languages": ["en"],
        "categories": [],
        "created_from": "upload"
    })
    
    # Statistics
    statistics = Column(JSON)
    
    # Access control
    is_public = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    shared_with = Column(JSON)  # List of user IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="datasets")
    
    def __repr__(self):
        return f"<UserDataset(id={self.id}, name={self.name}, user_id={self.user_id})>"

class UserModel(Base):
    __tablename__ = "user_models"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Model information
    model_type = Column(String(50), nullable=False)  # bart, pegasus, multilingual
    task = Column(String(50), nullable=False)  # summarization, simplification, translation
    base_model = Column(String(255))
    
    # Storage
    model_path = Column(String(500), nullable=False)
    config_path = Column(String(500))
    tokenizer_path = Column(String(500))
    
    # Training info
    training_job_id = Column(Integer, ForeignKey("training_jobs.id"))
    dataset_id = Column(Integer, ForeignKey("user_datasets.id"))
    
    # Metadata
    metadata_info = Column(JSON, default=lambda: {
        "epochs": 3,
        "batch_size": 4,
        "learning_rate": 5e-5,
        "metrics": {},
        "languages": ["en"]
    })
    
    # Access control
    is_public = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    shared_with = Column(JSON)  # List of user IDs
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="models")
    
    def __repr__(self):
        return f"<UserModel(id={self.id}, name={self.name}, model_type={self.model_type})>"

class InferenceRequest(Base):
    __tablename__ = "inference_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_id = Column(String(100), unique=True, nullable=False)
    
    # Request details
    model_id = Column(Integer, ForeignKey("user_models.id"))
    input_text = Column(Text, nullable=False)
    input_type = Column(String(50))  # text, pdf, document
    input_file_path = Column(String(500))
    
    # Parameters
    parameters = Column(JSON, default=lambda: {
        "max_length": 512,
        "min_length": 50,
        "temperature": 1.0,
        "num_beams": 4
    })
    
    # Results
    output_text = Column(Text)
    output_file_path = Column(String(500))
    metrics = Column(JSON)
    processing_time = Column(Float)  # in seconds
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<InferenceRequest(id={self.id}, request_id={self.request_id}, status={self.status})>"