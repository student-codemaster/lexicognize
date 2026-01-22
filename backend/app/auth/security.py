from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import secrets
import string
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.auth import crud, schemas

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify a JWT token and return payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
        
        return payload
    except JWTError:
        return None

def generate_api_key(length: int = 32) -> str:
    """Generate a random API key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_secret(length: int = 64) -> str:
    """Generate a random API secret."""
    return secrets.token_urlsafe(length)

def generate_password_reset_token() -> str:
    """Generate a password reset token."""
    return secrets.token_urlsafe(32)

def generate_email_verification_token() -> str:
    """Generate an email verification token."""
    return secrets.token_urlsafe(32)

def get_current_user(db: Session, token: str) -> Optional[schemas.UserInDB]:
    """Get current user from access token."""
    payload = verify_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    user = crud.get_user_by_id(db, user_id)
    if not user or user.status != schemas.UserStatus.ACTIVE:
        return None
    
    return user

def get_current_user_from_refresh_token(db: Session, token: str) -> Optional[schemas.UserInDB]:
    """Get current user from refresh token."""
    payload = verify_token(token, "refresh")
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    if not user_id:
        return None
    
    # Check if refresh token exists in database and is not revoked
    refresh_token = crud.get_refresh_token(db, token)
    if not refresh_token or refresh_token.is_revoked:
        return None
    
    user = crud.get_user_by_id(db, user_id)
    if not user or user.status != schemas.UserStatus.ACTIVE:
        return None
    
    return user

def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token."""
    refresh_token = crud.get_refresh_token(db, token)
    if not refresh_token:
        return False
    
    refresh_token.is_revoked = True
    db.commit()
    return True

def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> bool:
    """Revoke all refresh tokens for a user."""
    return crud.revoke_all_user_refresh_tokens(db, user_id)

def check_permissions(user: schemas.UserInDB, required_role: Optional[schemas.UserRole] = None) -> bool:
    """Check if user has required permissions."""
    if user.status != schemas.UserStatus.ACTIVE:
        return False
    
    if required_role:
        return user.role == required_role
    
    return True

def get_user_scopes(user: schemas.UserInDB) -> List[str]:
    """Get user scopes based on role."""
    scopes = ["read", "write"]
    
    if user.role == schemas.UserRole.ADMIN:
        scopes.extend(["admin", "manage_users", "manage_system"])
    elif user.role == schemas.UserRole.RESEARCHER:
        scopes.extend(["train_models", "manage_datasets"])
    elif user.role == schemas.UserRole.LEGAL_PROFESSIONAL:
        scopes.extend(["legal_access", "batch_processing"])
    
    return scopes

def create_tokens_for_user(user: schemas.UserInDB, db: Session) -> Dict[str, str]:
    """Create access and refresh tokens for a user."""
    # Create tokens
    access_token = create_access_token({
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "scopes": get_user_scopes(user)
    })
    
    refresh_token = create_refresh_token({
        "user_id": user.id
    })
    
    # Store refresh token in database
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    crud.create_refresh_token(db, user.id, refresh_token, expires_at)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }