import secrets
import hashlib
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.organization import APIKey
from app.schemas.api_key_schema import APIKeyCreate, APIKeyUpdate

def generate_api_key() -> Tuple[str, str, str]:
    """Returns (full_key, prefix, key_hash)"""
    prefix = "sk_live_"
    secret = secrets.token_urlsafe(32)
    full_key = f"{prefix}{secret}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, prefix, key_hash

async def create_api_key(db: AsyncSession, obj_in: APIKeyCreate, org_id: str) -> Tuple[APIKey, str]:
    full_key, prefix, key_hash = generate_api_key()
    db_obj = APIKey(
        org_id=org_id,
        key_prefix=prefix,
        key_hash=key_hash,
        name=obj_in.name,
        rate_limit_per_sec=obj_in.rate_limit_per_sec,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj, full_key

async def get_api_keys_by_org(db: AsyncSession, org_id: str) -> List[APIKey]:
    result = await db.execute(select(APIKey).filter(APIKey.org_id == org_id))
    return result.scalars().all()

async def get_api_key(db: AsyncSession, key_id: str) -> Optional[APIKey]:
    result = await db.execute(select(APIKey).filter(APIKey.id == key_id))
    return result.scalars().first()
