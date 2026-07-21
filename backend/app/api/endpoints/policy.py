from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.policy.engine import policy_engine

router = APIRouter()

class PolicySimulateRequest(BaseModel):
    user_context: Dict[str, Any]
    action: str
    resource_metadata: Dict[str, Any]

@router.post("/simulate")
def simulate_policy(req: PolicySimulateRequest):
    return policy_engine.simulate_policy(
        user_context=req.user_context,
        action=req.action,
        resource_metadata=req.resource_metadata
    )
