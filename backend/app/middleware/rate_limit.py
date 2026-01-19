from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Optional
import redis
from app.config import settings

# Initialize Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None

def get_user_identifier(request: Request) -> str:
    """Get user identifier for rate limiting."""
    # Try to get user ID from request state
    if hasattr(request.state, 'user_id'):
        return str(request.state.user_id)
    
    # Fall back to IP address
    return get_remote_address(request)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_user_identifier,
    storage_uri=settings.REDIS_URL if settings.REDIS_URL else "memory://",
    default_limits=["100/minute", "1000/hour"]
)

class RateLimitMiddleware:
    """Middleware for rate limiting."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        try:
            # Check rate limit
            endpoint = f"{request.method}:{request.url.path}"
            limit = limiter._rate_limit(endpoint, request)
            
            if limit:
                identifier = get_user_identifier(request)
                if not limiter._check_request_limit(request, identifier, endpoint):
                    raise RateLimitExceeded(identifier, endpoint)
        
        except RateLimitExceeded:
            # Handle rate limit exceeded
            response = _rate_limit_exceeded_handler(request, RateLimitExceeded)
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)