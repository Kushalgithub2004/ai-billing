from fastapi import APIRouter
from app.api.v1.endpoints import auth, api_keys, billing, usage, admin, demo

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api_keys"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
