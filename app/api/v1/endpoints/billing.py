from typing import Any, List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.services import billing_service
from app.models.user import User

router = APIRouter()

@router.post("/generate-invoice")
async def generate_invoice(
    org_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser), # Admin only
) -> Any:
    """
    Trigger invoice generation for an organization manually.
    """
    invoice = await billing_service.generate_invoice_for_org(db, org_id, start_date, end_date)
    return {"invoice_id": invoice.id, "total_amount": invoice.total_amount, "status": invoice.status}

@router.get("/invoices")
async def get_my_invoices(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List invoices for the current user's organization.
    """
    from app.models.organization import OrganizationMember
    result = await db.execute(select(OrganizationMember).filter(OrganizationMember.user_id == current_user.id))
    member = result.scalars().first()
    if not member:
         raise HTTPException(status_code=400, detail="User not in any organization")
         
    result = await db.execute(select(Invoice).filter(Invoice.org_id == member.org_id).order_by(Invoice.created_at.desc()))
    invoices = result.scalars().all()
    return invoices
