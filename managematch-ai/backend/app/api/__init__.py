from fastapi import APIRouter
from .v1.router import api_router as v1_router
from .routers.businesses import router as businesses_router
from .routers.managers import router as managers_router
from .routers.matches import router as matches_router

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")
api_router.include_router(businesses_router)
api_router.include_router(managers_router)
api_router.include_router(matches_router)
