from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.ai.router import ai_orchestrator

router = APIRouter()

class AIQueryRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    preferred_provider: Optional[str] = None

class AIQueryResponse(BaseModel):
    provider: str
    response: str
    tokens_used: int
    cost_usd: float
    status: str

@router.post("/generate", response_model=AIQueryResponse)
async def generate_ai_response(req: AIQueryRequest):
    try:
        res = await ai_orchestrator.execute_query(
            prompt=req.prompt,
            system_prompt=req.system_prompt,
            preferred_provider=req.preferred_provider
        )
        return AIQueryResponse(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )

@router.get("/providers")
def list_ai_providers():
    return {
        "providers": [p.provider_name for p in ai_orchestrator.providers]
    }
