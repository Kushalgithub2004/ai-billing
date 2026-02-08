from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.api import deps
from app.models.user import User
from app.models.usage import UsageLog
from app.models.organization import OrganizationMember

router = APIRouter()

@router.get("/summary")
async def get_usage_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get usage summary for the current user's organization.
    """
    # Get User's Org
    result = await db.execute(select(OrganizationMember).filter(OrganizationMember.user_id == current_user.id))
    member = result.scalars().first()
    if not member:
        raise HTTPException(status_code=400, detail="User not in any organization")
    
    # Query aggregated usage
    usage_query = select(
        UsageLog.endpoint,
        func.count(UsageLog.id).label("count"),
        func.date(UsageLog.timestamp).label("date")
    ).filter(
        UsageLog.org_id == member.org_id,
        func.date(UsageLog.timestamp) >= start_date,
        func.date(UsageLog.timestamp) <= end_date
    ).group_by(UsageLog.endpoint, func.date(UsageLog.timestamp))
    
    result = await db.execute(usage_query)
    data = result.all()
    
    # Format response
    summary = []
    for endpoint, count, day in data:
        summary.append({
            "endpoint": endpoint,
            "count": count,
            "date": day
        })
    return summary
