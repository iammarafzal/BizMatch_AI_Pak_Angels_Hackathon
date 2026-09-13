from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.business import Business
from app.schemas.business import BusinessResponse
from app.schemas.match import AnalyzeRequirementsRequest, AnalyzeRequirementsResponse
from app.services.ai_orchestrator import extract_business_requirements

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.get("/", response_model=list[BusinessResponse])
async def get_businesses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Business))
    return result.scalars().all()

@router.post("/analyze-requirements", response_model=AnalyzeRequirementsResponse)
async def analyze_requirements(req: AnalyzeRequirementsRequest):
    structured_data = extract_business_requirements(
        goals=req.goals,
        challenges=req.challenges,
        preferences=req.raw_preferences
    )
    return AnalyzeRequirementsResponse(success=True, data=structured_data)
