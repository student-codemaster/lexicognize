from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.auth import models, schemas
from app.auth.security import (
    verify_password, get_password_hash,
    generate_password_reset_token,
    generate_email_verification_token
)

# User CRUD operations
def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username."""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_username_or_email(db: Session, username_or_email: str) -> Optional[models.User]:
    """Get user by username or email."""
    return db.query(models.User).filter(
        or_(
            models.User.username == username_or_email,
            models.User.email == username_or_email
        )
    ).first()

def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
) -> List[models.User]:
    """Get users with filtering."""
    query = db.query(models.User)
    
    if role:
        query = query.filter(models.User.role == role)
    
    if status:
        query = query.filter(models.User.status == status)
    
    if search:
        query = query.filter(
            or_(
                models.User.username.ilike(f"%{search}%"),
                models.User.email.ilike(f"%{search}%"),
                models.User.full_name.ilike(f"%{search}%")
            )
        )
    
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user."""
    # Check if user already exists
    if get_user_by_email(db, user.email):
        raise ValueError("Email already registered")
    
    if get_user_by_username(db, user.username):
        raise ValueError("Username already taken")
    
    # Create user
    db_user = models.User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
        role=models.UserRole.USER,
        status=models.UserStatus.ACTIVE,
        preferences={
            "language": "en",
            "theme": "light",
            "notifications": True,
            "default_model": "bart"
        }
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update user information."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    
    return db_user

def update_user_last_login(db: Session, user_id: int) -> None:
    """Update user's last login timestamp."""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.last_login = datetime.utcnow()
        db.commit()

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user (soft delete by setting status to inactive)."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.status = models.UserStatus.INACTIVE
    db_user.updated_at = datetime.utcnow()
    db.commit()
    
    return True

def change_user_password(db: Session, user_id: int, new_password: str) -> bool:
    """Change user password."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.hashed_password = get_password_hash(new_password)
    db_user.updated_at = datetime.utcnow()
    db.commit()
    
    return True

def verify_user_password(db: Session, user_id: int, password: str) -> bool:
    """Verify user password."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    return verify_password(password, db_user.hashed_password)

# Refresh Token CRUD operations
def get_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    """Get refresh token by token string."""
    return db.query(models.RefreshToken).filter(
        models.RefreshToken.token == token
    ).first()

def create_refresh_token(
    db: Session,
    user_id: int,
    token: str,
    expires_at: datetime
) -> models.RefreshToken:
    """Create a new refresh token."""
    # Revoke existing tokens for the same user (optional: keep multiple devices)
    # revoke_all_user_refresh_tokens(db, user_id)
    
    db_token = models.RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        is_revoked=False
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token

def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token."""
    db_token = get_refresh_token(db, token)
    if not db_token:
        return False
    
    db_token.is_revoked = True
    db.commit()
    
    return True

def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> bool:
    """Revoke all refresh tokens for a user."""
    tokens = db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.is_revoked == False
    ).all()
    
    for token in tokens:
        token.is_revoked = True
    
    db.commit()
    return True

# Password Reset Token CRUD operations
def create_password_reset_token(db: Session, user_id: int) -> models.PasswordResetToken:
    """Create a password reset token."""
    # Delete existing tokens for this user
    db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.user_id == user_id
    ).delete()
    
    token = generate_password_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    db_token = models.PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        is_used=False
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token

def get_password_reset_token(db: Session, token: str) -> Optional[models.PasswordResetToken]:
    """Get password reset token by token string."""
    return db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token == token,
        models.PasswordResetToken.is_used == False,
        models.PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

def use_password_reset_token(db: Session, token: str) -> bool:
    """Mark a password reset token as used."""
    db_token = get_password_reset_token(db, token)
    if not db_token:
        return False
    
    db_token.is_used = True
    db.commit()
    
    return True

# Email Verification Token CRUD operations
def create_email_verification_token(db: Session, user_id: int) -> models.EmailVerificationToken:
    """Create an email verification token."""
    # Delete existing tokens for this user
    db.query(models.EmailVerificationToken).filter(
        models.EmailVerificationToken.user_id == user_id
    ).delete()
    
    token = generate_email_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=48)
    
    db_token = models.EmailVerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token

def get_email_verification_token(db: Session, token: str) -> Optional[models.EmailVerificationToken]:
    """Get email verification token by token string."""
    return db.query(models.EmailVerificationToken).filter(
        models.EmailVerificationToken.token == token,
        models.EmailVerificationToken.expires_at > datetime.utcnow()
    ).first()

def verify_user_email(db: Session, user_id: int) -> bool:
    """Mark user email as verified."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db_user.email_verified_at = datetime.utcnow()
    db.commit()
    
    return True

# API Key CRUD operations
def create_api_key(
    db: Session,
    user_id: int,
    api_key: schemas.ApiKeyCreate
) -> models.ApiKey:
    """Create a new API key."""
    import secrets
    import string
    
    # Generate API key and secret
    key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    secret = secrets.token_urlsafe(64)
    
    db_api_key = models.ApiKey(
        user_id=user_id,
        name=api_key.name,
        key=key,
        secret=secret,
        scopes=api_key.scopes,
        rate_limit=api_key.rate_limit,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return db_api_key

def get_api_key_by_key(db: Session, key: str) -> Optional[models.ApiKey]:
    """Get API key by key string."""
    return db.query(models.ApiKey).filter(
        models.ApiKey.key == key,
        models.ApiKey.is_active == True
    ).first()

def get_user_api_keys(db: Session, user_id: int) -> List[models.ApiKey]:
    """Get all API keys for a user."""
    return db.query(models.ApiKey).filter(
        models.ApiKey.user_id == user_id
    ).all()

def revoke_api_key(db: Session, api_key_id: int, user_id: int) -> bool:
    """Revoke an API key."""
    db_api_key = db.query(models.ApiKey).filter(
        models.ApiKey.id == api_key_id,
        models.ApiKey.user_id == user_id
    ).first()
    
    if not db_api_key:
        return False
    
    db_api_key.is_active = False
    db.commit()
    
    return True

def update_api_key_last_used(db: Session, api_key_id: int) -> None:
    """Update API key last used timestamp."""
    db_api_key = db.query(models.ApiKey).filter(
        models.ApiKey.id == api_key_id
    ).first()
    
    if db_api_key:
        db_api_key.last_used = datetime.utcnow()
        db.commit()

# Statistics and analytics
def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
    """Get user statistics."""
    stats = {}
    
    # Count datasets
    stats['total_datasets'] = db.query(models.UserDataset).filter(
        models.UserDataset.user_id == user_id
    ).count()
    
    # Count models
    stats['total_models'] = db.query(models.UserModel).filter(
        models.UserModel.user_id == user_id
    ).count()
    
    # Count training jobs
    stats['total_training_jobs'] = db.query(models.TrainingJob).filter(
        models.TrainingJob.user_id == user_id
    ).count()
    
    # Count inference requests
    stats['total_inference_requests'] = db.query(models.InferenceRequest).filter(
        models.InferenceRequest.user_id == user_id
    ).count()
    
    # Get storage usage (simplified)
    datasets_size = db.query(models.UserDataset.file_size).filter(
        models.UserDataset.user_id == user_id
    ).all()
    stats['storage_used'] = sum([size[0] for size in datasets_size if size[0]])
    
    # Last activity
    last_activity = db.query(
        db.func.greatest(
            models.User.last_login,
            models.TrainingJob.updated_at,
            models.InferenceRequest.created_at
        )
    ).filter(
        models.User.id == user_id
    ).scalar()
    
    stats['last_activity'] = last_activity
    
    return stats

# Search and filtering
def search_users(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 50
) -> List[models.User]:
    """Search users by username, email, or full name."""
    return db.query(models.User).filter(
        or_(
            models.User.username.ilike(f"%{query}%"),
            models.User.email.ilike(f"%{query}%"),
            models.User.full_name.ilike(f"%{query}%")
        ),
        models.User.status == models.UserStatus.ACTIVE
    ).offset(skip).limit(limit).all()