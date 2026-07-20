from fastapi import APIRouter
from app.api.endpoints import auth, knowledge

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
