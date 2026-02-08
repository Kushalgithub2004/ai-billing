from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.crud import crud_api_key
from app.schemas.api_key_schema import APIKey, APIKeyCreate, APIKeyResponse
from app.models.user import User
from app.models.organization import Organization
from sqlalchemy.future import select

router = APIRouter()

@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    api_key_in: APIKeyCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new API key for the user's organization.
    For simplicity, assuming user belongs to one organization or we pick the first one.
    Real world would require selecting the org context.
    """
    # Fetch user's org
    # This requires `users` relationship in Organization or vice versa.
    # We defined OrganizationMember. Let's fetch it.
    from app.models.organization import OrganizationMember
    result = await db.execute(select(OrganizationMember).filter(OrganizationMember.user_id == current_user.id))
    member = result.scalars().first()
    
    if not member:
         raise HTTPException(status_code=400, detail="User does not belong to any organization")
    
    api_key, full_key = await crud_api_key.create_api_key(db, api_key_in, str(member.org_id))
    
    # We can't return full_key directly on APIKey model as it's not stored.
    # We use APIKeyResponse which inherits and adds full_key
    response = APIKeyResponse.model_validate(api_key)
    response.full_key = full_key
    return response

@router.get("/", response_model=List[APIKey])
async def read_api_keys(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve API keys.
    """
    from app.models.organization import OrganizationMember
    result = await db.execute(select(OrganizationMember).filter(OrganizationMember.user_id == current_user.id))
    member = result.scalars().first()
    
    if not member:
        return []
        
    return await crud_api_key.get_api_keys_by_org(db, org_id=member.org_id)
