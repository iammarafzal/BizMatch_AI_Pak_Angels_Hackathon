from fastapi import APIRouter
from .v1.router import api_router as v1_router

api_router = APIRouter()

# Mount v1 router at /v1 prefix as well as base /api prefix for flexibility
api_router.include_router(v1_router, prefix="/v1")
api_router.include_router(v1_router)
