import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.business import Business
from app.models.manager import Manager
from app.models.match import MatchRecord
from app.schemas.manager import ManagerResponse
from app.schemas.match import (
    CalculateMatchesRequest,
    BatchMatchResponse,
    CandidateMatchSummary,
    MatchFactorScores,
    ExplainMatchRequest,
    ExplainMatchResponse,
    MatchRecordResponse,
)
from app.engine.matcher import rank_managers_for_business, calculate_match
from app.services.ai_orchestrator import generate_match_explanation

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/calculate", response_model=BatchMatchResponse)
async def calculate_matches(
    req: CalculateMatchesRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate deterministic compatibility scores between a business and all candidate managers.
    Accepts either an existing 'business_id' OR an inline 'business_data' payload.
    """
    if not req.business_id and not req.business_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'business_id' or 'business_data'"
        )

    business_obj = None
    persisted_in_db = False

    # 1. Resolve business profile
    if req.business_id:
        result = await db.execute(select(Business).filter(Business.id == req.business_id))
        business_obj = result.scalars().first()
        if not business_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business with ID '{req.business_id}' not found"
            )
        persisted_in_db = True
    elif req.business_data:
        data = req.business_data.model_dump()
        budget = data.get("salary_budget")
        if budget is None:
            budget = data.get("monthly_budget_usd", 0.0)
            
        challenges = data.get("challenges") or data.get("core_problem", "")
        goals = data.get("goals")
        if not goals and data.get("primary_goals"):
            goals = " ".join(data["primary_goals"])

        business_obj = Business(
            id=str(uuid.uuid4()),
            name=data["name"],
            industry=data["industry"],
            size=data.get("size"),
            stage=data.get("stage"),
            location=data.get("location"),
            employee_count=data.get("employee_count"),
            business_model=data.get("business_model"),
            goals=goals,
            challenges=challenges,
            required_skills=data.get("required_skills", []),
            required_experience=data.get("required_experience", []),
            leadership_requirements=data.get("leadership_requirements"),
            salary_budget=float(budget or 0.0),
            work_arrangement=data.get("work_arrangement"),
        )
        # We can also persist this new business in DB so historical records can reference it
        db.add(business_obj)
        await db.commit()
        await db.refresh(business_obj)
        persisted_in_db = True

    # 2. Fetch all managers from the database
    mgr_result = await db.execute(select(Manager))
    all_managers = mgr_result.scalars().all()
    
    if not all_managers:
        return BatchMatchResponse(
            business_id=business_obj.id,
            total_evaluated=0,
            matches=[]
        )

    # 3. Deterministic batch ranking
    ranked = rank_managers_for_business(business_obj, all_managers, limit=15)

    # 4. Format match summaries
    matches_summary: List[CandidateMatchSummary] = []
    for r in ranked:
        mgr_schema = ManagerResponse.model_validate(r.manager)
        factors = MatchFactorScores(
            industry_fit=r.factor_scores["industry_fit"],
            skills_fit=r.factor_scores["skills_fit"],
            experience_fit=r.factor_scores["experience_fit"],
            leadership_fit=r.factor_scores["leadership_fit"],
            stage_fit=r.factor_scores["stage_fit"],
            salary_fit=r.factor_scores["salary_fit"],
        )
        matches_summary.append(CandidateMatchSummary(
            manager=mgr_schema,
            overall_score=r.overall_score,
            factor_scores=factors
        ))

    # 5. Persist top matches if business is stored in DB
    if persisted_in_db:
        for r in ranked[:10]:
            match_rec = MatchRecord(
                id=str(uuid.uuid4()),
                business_id=business_obj.id,
                manager_id=r.manager_id,
                overall_score=r.overall_score,
                factor_scores=r.factor_scores,
                created_at=datetime.now(timezone.utc)
            )
            db.add(match_rec)
        await db.commit()

    return BatchMatchResponse(
        business_id=business_obj.id,
        total_evaluated=len(all_managers),
        matches=matches_summary
    )

@router.get("/{business_id}", response_model=List[MatchRecordResponse])
async def get_matches_for_business(
    business_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve historical match records for a business.
    """
    biz_result = await db.execute(select(Business).filter(Business.id == business_id))
    biz = biz_result.scalars().first()
    if not biz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID '{business_id}' not found"
        )

    query = select(MatchRecord).filter(MatchRecord.business_id == business_id).order_by(MatchRecord.overall_score.desc())
    result = await db.execute(query)
    records = result.scalars().all()
    return records

@router.post("/explain", response_model=ExplainMatchResponse)
async def explain_match(
    req: ExplainMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate explainable decision support card for a selected candidate.
    """
    biz_result = await db.execute(select(Business).filter(Business.id == req.business_id))
    biz = biz_result.scalars().first()
    
    mgr_result = await db.execute(select(Manager).filter(Manager.id == req.manager_id))
    mgr = mgr_result.scalars().first()
    
    if not biz or not mgr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business or Manager not found")

    match_result = calculate_match(biz, mgr)

    goals = getattr(biz, "goals", None) or getattr(biz, "primary_goals", [])
    if isinstance(goals, str):
        goals = [goals]

    biz_dict = {
        "name": biz.name,
        "industry": biz.industry,
        "stage": biz.stage,
        "goals": goals,
        "skills": getattr(biz, "required_skills", []) or []
    }

    mgr_dict = {
        "name": mgr.name,
        "title": getattr(mgr, "title", None) or getattr(mgr, "role_title", ""),
        "industries": getattr(mgr, "industries", []) or [],
        "stages": getattr(mgr, "verified_stages", None) or getattr(mgr, "industries", []),
        "skills": getattr(mgr, "skills", None) or getattr(mgr, "core_skills", []),
        "experience": getattr(mgr, "management_experience", None) or getattr(mgr, "verified_track_record", "")
    }

    analysis = await generate_match_explanation(
        business=biz_dict,
        manager=mgr_dict,
        scores=match_result.factor_scores
    )

    return ExplainMatchResponse(success=True, data=analysis)
