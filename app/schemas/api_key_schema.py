from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class APIKeyBase(BaseModel):
    name: Optional[str] = None
    rate_limit_per_sec: Optional[int] = 5
    is_active: Optional[bool] = True

class APIKeyCreate(APIKeyBase):
    name: str

class APIKeyUpdate(APIKeyBase):
    pass

class APIKeyInDBBase(APIKeyBase):
    id: UUID
    org_id: UUID
    key_prefix: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class APIKey(APIKeyInDBBase):
    pass

class APIKeyResponse(APIKey):
    full_key: Optional[str] = None # Only returned on creation
