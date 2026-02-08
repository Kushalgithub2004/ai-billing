import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.redis import get_redis_client
from app.api import deps
from app.db.session import AsyncSessionLocal
from sqlalchemy.future import select
from app.models.organization import APIKey

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only rate limit if API Key is present.
        # Auth middleware (or logic) usually validates key.
        # But middleware order matters. 
        # If we put this BEFORE Auth, we extract key manually.
        api_key_header = request.headers.get("X-API-KEY")
        
        if api_key_header:
            client = await get_redis_client()
            # Simple fixed window rate limiting
            # Key: prefix + api_key_hash + timestamp_window
            
            # First, we need to know the limit for this key.
            # Querying DB for every request is slow. 
            # We should cache the limit in Redis too.
            
            hashed_key = self.hash_key(api_key_header)
            cache_key_meta = f"apikey:meta:{hashed_key}"
            
            # Check if we have limit in cache
            limit = await client.get(cache_key_meta)
            
            if not limit:
                 async with AsyncSessionLocal() as db:
                    result = await db.execute(select(APIKey).filter(APIKey.key_hash == hashed_key))
                    api_key_obj = result.scalars().first()
                    if api_key_obj:
                        limit = api_key_obj.rate_limit_per_sec
                        # Cache metadata for 5 minutes
                        await client.setex(cache_key_meta, 300, limit)
                    else:
                        # Invalid key, let Auth middleware handle it or return 401 here?
                        # Best to pass through to Auth middleware to handle 401 consistently.
                        # OR if we want to save resources, block here.
                        # Let's pass through.
                        return await call_next(request)
            
            limit = int(limit)
            
            # Rate Limit Logic: Fixed Window (1 second)
            current_second = int(time.time())
            rate_key = f"rate:{hashed_key}:{current_second}"
            
            # Increment
            request_count = await client.incr(rate_key)
            
            # Set expiry if new key
            if request_count == 1:
                await client.expire(rate_key, 5) # 5 seconds just to be safe
                
            if request_count > limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
        
        return await call_next(request)

    def hash_key(self, key: str) -> str:
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
