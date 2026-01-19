from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database.session import get_db
from app.auth import crud, schemas
from app.auth.security import check_permissions

logger = logging.getLogger(__name__)

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def api_key_auth(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[schemas.UserInDB]:
    """Authenticate using API key."""
    if not api_key:
        return None
    
    # Get API key from database
    db_api_key = crud.get_api_key_by_key(db, api_key)
    if not db_api_key or not db_api_key.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # Check if API key is expired
    if db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="API key expired"
        )
    
    # Get user
    user = crud.get_user_by_id(db, db_api_key.user_id)
    if not user or user.status != schemas.UserStatus.ACTIVE:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )
    
    # Update last used timestamp
    crud.update_api_key_last_used(db, db_api_key.id)
    
    # Set user in request state
    request.state.user_id = user.id
    request.state.user = user
    request.state.api_key = db_api_key
    
    return user

class APIKeyAuthMiddleware:
    """Middleware for API key authentication."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        
        if api_key:
            # Create a mock dependency context
            from fastapi import Depends
            from app.database.session import SessionLocal
            
            db = SessionLocal()
            try:
                user = await api_key_auth(request, api_key, db)
                if user:
                    request.state.user = user
                    request.state.auth_method = "api_key"
            except HTTPException:
                pass
            finally:
                db.close()
        
        await self.app(scope, receive, send)