from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.auth import schemas, crud, security
from app.auth.security import (
    get_current_user,
    create_tokens_for_user,
    revoke_refresh_token,
    revoke_all_user_refresh_tokens
)
from app.config import settings

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register", response_model=schemas.UserPublic)
async def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Register a new user."""
    try:
        # Create user
        db_user = crud.create_user(db, user)
        
        # Create email verification token
        verification_token = crud.create_email_verification_token(db, db_user.id)
        
        # TODO: Send verification email (implement email service)
        # if background_tasks:
        #     background_tasks.add_task(
        #         send_verification_email,
        #         db_user.email,
        #         verification_token.token
        #     )
        
        return db_user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login user and return tokens."""
    # Get user by username or email
    user = crud.get_user_by_username_or_email(db, form_data.username_or_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check password
    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check user status
    if user.status != schemas.UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    
    # Update last login
    crud.update_user_last_login(db, user.id)
    
    # Create tokens
    tokens = create_tokens_for_user(user, db)
    
    return tokens

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    refresh_request: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Verify refresh token and get user
    user = security.get_current_user_from_refresh_token(db, refresh_request.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Revoke old refresh token
    security.revoke_refresh_token(db, refresh_request.refresh_token)
    
    # Create new tokens
    tokens = create_tokens_for_user(user, db)
    
    return tokens

@router.post("/logout")
async def logout(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Logout user by revoking refresh token."""
    success = security.revoke_refresh_token(db, refresh_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )
    
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all(
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout from all devices by revoking all refresh tokens."""
    success = security.revoke_all_user_refresh_tokens(db, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to logout from all devices"
        )
    
    return {"message": "Successfully logged out from all devices"}

@router.get("/me", response_model=schemas.UserPublic)
async def get_current_user_info(
    current_user: schemas.UserInDB = Depends(get_current_user)
):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=schemas.UserPublic)
async def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    updated_user = crud.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.post("/change-password")
async def change_password(
    password_data: schemas.ChangePasswordRequest,
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    # Verify current password
    if not crud.verify_user_password(db, current_user.id, password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Change password
    success = crud.change_user_password(db, current_user.id, password_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
    
    # Revoke all refresh tokens (optional security measure)
    security.revoke_all_user_refresh_tokens(db, current_user.id)
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(
    reset_request: schemas.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset."""
    user = crud.get_user_by_email(db, reset_request.email)
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If the email exists, a reset link will be sent"}
    
    # Create password reset token
    reset_token = crud.create_password_reset_token(db, user.id)
    
    # TODO: Send password reset email
    # background_tasks.add_task(
    #     send_password_reset_email,
    #     user.email,
    #     reset_token.token
    # )
    
    return {"message": "If the email exists, a reset link will be sent"}

@router.post("/reset-password")
async def reset_password(
    reset_data: schemas.PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using token."""
    # Get reset token
    reset_token = crud.get_password_reset_token(db, reset_data.token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Change password
    success = crud.change_user_password(db, reset_token.user_id, reset_data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
    
    # Mark token as used
    crud.use_password_reset_token(db, reset_data.token)
    
    # Revoke all refresh tokens
    security.revoke_all_user_refresh_tokens(db, reset_token.user_id)
    
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(
    verification_request: schemas.EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify email using token."""
    # Get verification token
    verification_token = crud.get_email_verification_token(db, verification_request.token)
    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Verify email
    success = crud.verify_user_email(db, verification_token.user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify email"
        )
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(
    background_tasks: BackgroundTasks,
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend email verification."""
    if current_user.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Create new verification token
    verification_token = crud.create_email_verification_token(db, current_user.id)
    
    # TODO: Send verification email
    # background_tasks.add_task(
    #     send_verification_email,
    #     current_user.email,
    #     verification_token.token
    # )
    
    return {"message": "Verification email sent"}

# API Key Management
@router.post("/api-keys", response_model=schemas.ApiKeyPublic)
async def create_api_key(
    api_key: schemas.ApiKeyCreate,
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key."""
    db_api_key = crud.create_api_key(db, current_user.id, api_key)
    
    # Return public info (without secret)
    return schemas.ApiKeyPublic(
        id=db_api_key.id,
        name=db_api_key.name,
        key=db_api_key.key,
        scopes=db_api_key.scopes,
        rate_limit=db_api_key.rate_limit,
        is_active=db_api_key.is_active,
        last_used=db_api_key.last_used,
        expires_at=db_api_key.expires_at,
        created_at=db_api_key.created_at
    )

@router.get("/api-keys", response_model=List[schemas.ApiKeyPublic])
async def get_api_keys(
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all API keys for current user."""
    db_api_keys = crud.get_user_api_keys(db, current_user.id)
    
    # Convert to public schema
    return [
        schemas.ApiKeyPublic(
            id=key.id,
            name=key.name,
            key=key.key,
            scopes=key.scopes,
            rate_limit=key.rate_limit,
            is_active=key.is_active,
            last_used=key.last_used,
            expires_at=key.expires_at,
            created_at=key.created_at
        )
        for key in db_api_keys
    ]

@router.delete("/api-keys/{api_key_id}")
async def revoke_api_key(
    api_key_id: int,
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key."""
    success = crud.revoke_api_key(db, api_key_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key revoked successfully"}

# Admin endpoints
@router.get("/users", response_model=List[schemas.UserPublic])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get users (admin only)."""
    if current_user.role != schemas.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    users = crud.get_users(db, skip=skip, limit=limit, role=role, status=status, search=search)
    return users

@router.get("/stats")
async def get_user_stats(
    current_user: schemas.UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    stats = crud.get_user_stats(db, current_user.id)
    return stats

# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth"}