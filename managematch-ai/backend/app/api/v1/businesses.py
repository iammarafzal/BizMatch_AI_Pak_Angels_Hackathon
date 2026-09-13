import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessResponse
from app.schemas.match import AnalyzeRequirementsRequest, AnalyzeRequirementsResponse
from app.services.ai_orchestrator import extract_business_requirements

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    payload: BusinessCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new business profile in the database.
    """
    biz_dict = payload.model_dump()
    
    # Resolve fields between standard Task 2 model and compat aliases
    budget = biz_dict.get("salary_budget")
    if budget is None:
        budget = biz_dict.get("monthly_budget_usd", 0.0)
        
    challenges = biz_dict.get("challenges") or biz_dict.get("core_problem", "")
    goals = biz_dict.get("goals")
    if not goals and biz_dict.get("primary_goals"):
        goals = " ".join(biz_dict["primary_goals"])
        
    new_biz = Business(
        id=str(uuid.uuid4()),
        name=biz_dict["name"],
        industry=biz_dict["industry"],
        size=biz_dict.get("size"),
        stage=biz_dict.get("stage"),
        location=biz_dict.get("location"),
        employee_count=biz_dict.get("employee_count"),
        business_model=biz_dict.get("business_model"),
        goals=goals,
        challenges=challenges,
        required_skills=biz_dict.get("required_skills", []),
        required_experience=biz_dict.get("required_experience", []),
        leadership_requirements=biz_dict.get("leadership_requirements"),
        salary_budget=float(budget or 0.0),
        work_arrangement=biz_dict.get("work_arrangement"),
    )
    
    db.add(new_biz)
    await db.commit()
    await db.refresh(new_biz)
    
    return new_biz

@router.get("/", response_model=List[BusinessResponse])
async def get_businesses(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all seeded and user-created businesses.
    """
    result = await db.execute(select(Business))
    return result.scalars().all()

@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business_by_id(
    business_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a single business profile by ID.
    """
    result = await db.execute(select(Business).filter(Business.id == business_id))
    biz = result.scalars().first()
    if not biz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID '{business_id}' not found"
        )
    return biz

@router.post("/analyze-requirements", response_model=AnalyzeRequirementsResponse)
async def analyze_requirements(req: AnalyzeRequirementsRequest):
    """
    Parse unstructured business goals and challenges into structured requirements.
    """
    structured_data = extract_business_requirements(
        goals=req.goals,
        challenges=req.challenges,
        preferences=req.raw_preferences
    )
    return AnalyzeRequirementsResponse(success=True, data=structured_data)
