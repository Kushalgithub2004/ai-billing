from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from app.middleware.usage_tracker import UsageTrackingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(UsageTrackingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "SaaS Billing Backend is running"}
