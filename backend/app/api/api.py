from fastapi import APIRouter
from app.api.endpoints import auth, knowledge, ai, graph, governance, policy

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai_orchestrator"])
api_router.include_router(graph.router, prefix="/graph", tags=["knowledge_graph"])
api_router.include_router(governance.router, prefix="/governance", tags=["data_governance"])
api_router.include_router(policy.router, prefix="/policy", tags=["policy_engine"])
