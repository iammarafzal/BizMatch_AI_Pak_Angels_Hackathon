from fastapi import APIRouter
from .businesses import router as businesses_router
from .managers import router as managers_router
from .matches import router as matches_router
from .requirements import router as requirements_router

api_router = APIRouter()

api_router.include_router(businesses_router)
api_router.include_router(managers_router)
api_router.include_router(matches_router)
api_router.include_router(requirements_router)
