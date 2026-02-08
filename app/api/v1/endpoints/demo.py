from fastapi import APIRouter, Depends
from typing import Any

router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any
from app.services import ai_service
from app.api import deps
from app.models.user import User

router = APIRouter()

class GenerationRequest(BaseModel):
    prompt: str
    max_length: int = 50

@router.post("/generate")
async def generate_ai_text(
    request: GenerationRequest,
    # Valid API Key required via middleware (already enforced globally or we can add dependency if we want strict user context)
    # The RateLimit middleware handles the key check.
    # But often we want to know WHO is calling to bill them properly?
    # The middleware logs usage by API Key. So billing is handled!
    # We just need to ensure authentication if required, or open access if key provided.
    # Auth middleware puts user in request.state if valid key? 
    # Our design: RateLimitMW checks limit. AuthMW checks validity.
    # So we are safe.
) -> Any:
    """
    Generate text using a local AI model (DistilGPT-2).
    """
    try:
        generated_text = await ai_service.generate_text(request.prompt, request.max_length)
        return {"generated_text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
