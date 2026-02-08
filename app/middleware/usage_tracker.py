import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.future import select
from app.db.session import AsyncSessionLocal
from app.models.organization import APIKey
from app.models.usage import UsageLog

class UsageTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract API Key
        api_key_header = request.headers.get("X-API-KEY")
        
        response = await call_next(request)
        
        if api_key_header:
            from starlette.background import BackgroundTask
            
            # If the response already has a background task, we need to chain them or handle it.
            # For simplicity, we wrap the existing task if any.
            # But usually, middleware is the outer layer.
            
            # We can also use FASTAPI's BackgroundTasks if we inject it, but middleware is lower level.
            # Starlette Response object has a .background attribute.
            
            existing_task = response.background
            
            async def task_wrapper():
                if existing_task:
                    await existing_task()
                await self.log_usage(api_key_header, request.url.path, request.method, response.status_code)
            
            response.background = BackgroundTask(task_wrapper)
                
        return response

    async def log_usage(self, api_key_value: str, endpoint: str, method: str, status_code: int):
        async with AsyncSessionLocal() as db:
            # Find API Key
            # In production, cache this lookup!
            result = await db.execute(select(APIKey).filter(APIKey.key_hash == self.hash_key(api_key_value)))
            # Wait, we store hash. Client sends full key. We need to hash it to look it up?
            # Or we store prefix? 
            # In `crud_api_key.py`, we generated `full_key` (prefix + secret) and stored `key_hash` (sha256 of full_key).
            # So we must hash the incoming key to find it.
            
            # Correction: The validation logic is:
            # 1. Provide X-API-KEY: sk_live_...
            # 2. Hash it.
            # 3. Look up in DB.
            
            hashed_key = self.hash_key(api_key_value)
            result = await db.execute(select(APIKey).filter(APIKey.key_hash == hashed_key))
            api_key_obj = result.scalars().first()
            
            if api_key_obj:
                usage = UsageLog(
                    org_id=api_key_obj.org_id,
                    api_key_id=api_key_obj.id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    cost_multiplier=1.0 # Logic to determine cost could be here
                )
                db.add(usage)
                await db.commit()

    def hash_key(self, key: str) -> str:
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
