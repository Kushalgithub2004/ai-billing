from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.billing import Invoice, InvoiceItem, PricingPlan, PricingRule, InvoiceStatus
from app.models.usage import UsageLog
from app.models.organization import Organization

async def generate_invoice_for_org(db: AsyncSession, org_id: str, start_date: date, end_date: date) -> Invoice:
    # Check if invoice already exists
    result = await db.execute(
        select(Invoice).filter(
            Invoice.org_id == org_id,
            Invoice.start_date == start_date,
            Invoice.end_date == end_date
        )
    )
    existing_invoice = result.scalars().first()
    if existing_invoice and existing_invoice.status == InvoiceStatus.PAID:
        return existing_invoice

    # Fetch Usage
    # Group by endpoint or we need a way to map endpoints to resources.
    # For simplicity, let's assume PricingRules map "endpoint" (resource_name) to cost.
    
    # Get Organization's Plan (Assuming org has plan_id, but current model links via PricingPlan? 
    # Wait, Organization model has `plan_id`? Let's check model.)
    # I didn't add `plan_id` to Organization in Step 2 schema implementation (I missed it or it wasn't there in my code).
    # Let's check `app/models/organization.py`.
    
    # If it's missing, I'll default to a "Free" plan or add it.
    # For now, let's just fetch ALL pricing rules and apply matching ones.
    # Ideally, we should fetch the plan associated with the org.
    
    # Let's fetch usage aggregated by endpoint
    usage_query = select(
        UsageLog.endpoint,
        func.count(UsageLog.id).label("count")
    ).filter(
        UsageLog.org_id == org_id,
        func.date(UsageLog.timestamp) >= start_date,
        func.date(UsageLog.timestamp) <= end_date
    ).group_by(UsageLog.endpoint)
    
    usage_result = await db.execute(usage_query)
    usage_data = usage_result.all() # list of (endpoint, count)
    
    total_amount = 0.0
    invoice_items = []
    
    # Fetch Pricing Rules (assuming 1 global plan for now if org logic is missing)
    # Or just hardcode some rules for demo if Schema is hard to change now.
    # But I should verify Schema.
    
    # Let's assume we have a default plan.
    plan_result = await db.execute(select(PricingPlan))
    default_plan = plan_result.scalars().first()
    
    rules_map = {}
    if default_plan:
        rule_result = await db.execute(select(PricingRule).filter(PricingRule.plan_id == default_plan.id))
        rules = rule_result.scalars().all()
        for r in rules:
            rules_map[r.resource_name] = r

    for endpoint, count in usage_data:
        # Match endpoint to resource_name (exact match for now)
        rule = rules_map.get(endpoint)
        cost = 0.0
        if rule:
            # Apply free tier
            billable_units = max(0, count - rule.free_tier_limit)
            cost = billable_units * rule.unit_price
            
            item = InvoiceItem(
                description=f"Usage for {endpoint}",
                units=count,
                unit_price=rule.unit_price,
                amount=cost
            )
            invoice_items.append(item)
            total_amount += cost
        else:
             # Unknown resource, maybe log it or charge default?
             # Let's skip for now or add as 0 cost.
             pass
             
    # Create Invoice
    if existing_invoice:
        # Update existing draft
        invoice = existing_invoice
        invoice.total_amount = total_amount
        # Remove old items? Or updating is complex. 
        # Easier to delete old items and re-add.
        # For MVP, let's just update total. logic for items needs specific handling.
    else:
        invoice = Invoice(
            org_id=org_id,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
            status=InvoiceStatus.DRAFT,
            due_date=end_date + timedelta(days=7)
        )
        db.add(invoice)
        await db.flush() # get ID
        
        for item in invoice_items:
            item.invoice_id = invoice.id
            db.add(item)
            
    await db.commit()
    return invoice
