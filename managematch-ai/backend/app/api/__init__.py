from fastapi import APIRouter
from .routers.businesses import router as businesses_router
from .routers.managers import router as managers_router
from .routers.matches import router as matches_router

api_router = APIRouter()
api_router.include_router(businesses_router)
api_router.include_router(managers_router)
api_router.include_router(matches_router)
