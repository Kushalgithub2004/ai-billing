from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.api import deps
from app.models.user import User
from app.models.usage import UsageLog
from app.models.organization import Organization

router = APIRouter()

@router.get("/analytics")
async def get_admin_analytics(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get system-wide analytics (Admin only).
    """
    # Total Orgs
    # Total Users
    # Total Usage (Last 24h, 30d)
    
    org_count = await db.scalar(select(func.count(Organization.id)))
    user_count = await db.scalar(select(func.count(User.id)))
    
    # Usage last 24h
    usage_24h = await db.scalar(
        select(func.count(UsageLog.id)).filter(
            UsageLog.timestamp >= func.now() - func.interval('1 day')
        )
    )
    
    return {
        "total_organizations": org_count,
        "total_users": user_count,
        "usage_last_24h": usage_24h
    }
