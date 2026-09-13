from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.business import Business
from app.models.manager import Manager
from app.schemas.match import (
    CalculateMatchesRequest, CalculateMatchesResponse,
    ExplainMatchRequest, ExplainMatchResponse,
    MatchRecordResponse
)
from app.services.deterministic import ScoringEngine
from app.services.ai_orchestrator import generate_match_explanation

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/calculate", response_model=CalculateMatchesResponse)
async def calculate_matches(
    req: CalculateMatchesRequest,
    db: AsyncSession = Depends(get_db)
):
    biz_result = await db.execute(select(Business).filter(Business.id == req.business_id))
    biz = biz_result.scalars().first()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
        
    mgr_result = await db.execute(select(Manager))
    managers = mgr_result.scalars().all()
    
    engine = ScoringEngine()
    ranked = await engine.compute_matches_for_business(biz, managers)
    
    response_data = []
    for idx, match in enumerate(ranked):
        response_data.append(MatchRecordResponse(
            id=f"match_{idx}",
            business_id=biz.id,
            manager_id=match["manager"].id,
            overall_score=match["overall_score"],
            factor_scores=match["factor_scores"],
            created_at=datetime.now(timezone.utc)
        ))
        
    return CalculateMatchesResponse(success=True, data=response_data)

@router.post("/explain", response_model=ExplainMatchResponse)
async def explain_match(
    req: ExplainMatchRequest,
    db: AsyncSession = Depends(get_db)
):
    biz_result = await db.execute(select(Business).filter(Business.id == req.business_id))
    biz = biz_result.scalars().first()
    
    mgr_result = await db.execute(select(Manager).filter(Manager.id == req.manager_id))
    mgr = mgr_result.scalars().first()
    
    if not biz or not mgr:
        raise HTTPException(status_code=404, detail="Business or Manager not found")
        
    # Recalculate deterministic score to feed AI
    engine = ScoringEngine()
    matches = await engine.compute_matches_for_business(biz, [mgr], limit=1)
    if not matches:
        raise HTTPException(status_code=400, detail="Could not score match")
        
    match_data = matches[0]
    
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
        scores=match_data["factor_scores"]
    )
    
    return ExplainMatchResponse(success=True, data=analysis)
