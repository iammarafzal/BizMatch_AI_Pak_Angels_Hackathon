import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.business import Business
from app.models.manager import Manager
from app.models.match import MatchRecord
from app.schemas.manager import ManagerResponse
from app.schemas.explanation import (
    ExplainMatchRequest,
    ExplainMatchResponse,
)
from app.schemas.match import (
    CalculateMatchesRequest,
    BatchMatchResponse,
    CandidateMatchSummary,
    MatchFactorScores,
    MatchRecordResponse,
)
from app.engine.matcher import rank_managers_for_business, calculate_match
from app.services.ai import run_explainability_pipeline

from app.core.dependencies import get_current_user, get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/matches", tags=["Matches"])


def _build_business_dict(biz: Business) -> Dict[str, Any]:
    """Helper to convert Business model to dictionary for AI services."""
    goals = getattr(biz, "goals", "")
    if not goals and getattr(biz, "primary_goals", None):
        goals = " ".join(biz.primary_goals)
    challenges = getattr(biz, "challenges", "") or getattr(biz, "core_problem", "")

    return {
        "id": biz.id,
        "name": biz.name,
        "industry": biz.industry,
        "stage": biz.stage,
        "size": getattr(biz, "size", None),
        "location": getattr(biz, "location", None),
        "salary_budget": float(getattr(biz, "salary_budget", 0.0) or getattr(biz, "monthly_budget_usd", 0.0) or 0.0),
        "goals": goals,
        "challenges": challenges,
        "required_skills": getattr(biz, "required_skills", []) or [],
        "required_experience": getattr(biz, "required_experience", []) or [],
        "leadership_requirements": getattr(biz, "leadership_requirements", None),
        "work_arrangement": getattr(biz, "work_arrangement", None),
    }


def _build_manager_dict(mgr: Manager) -> Dict[str, Any]:
    """Helper to convert Manager model to dictionary for AI services."""
    return {
        "id": mgr.id,
        "name": mgr.name,
        "role_title": getattr(mgr, "role_title", "") or getattr(mgr, "title", "Operations Manager"),
        "experience_years": getattr(mgr, "experience_years", 0),
        "expected_salary": float(getattr(mgr, "expected_salary", 0.0) or 0.0),
        "work_arrangement": getattr(mgr, "work_arrangement", None),
        "location": getattr(mgr, "location", None),
        "industries": getattr(mgr, "industries", []) or [],
        "skills": getattr(mgr, "skills", []) or getattr(mgr, "core_skills", []),
        "previous_roles": getattr(mgr, "previous_roles", []) or [],
        "achievements": getattr(mgr, "achievements", []) or [],
        "verified_stages": getattr(mgr, "verified_stages", []) or [],
        "bio": getattr(mgr, "bio", ""),
        "verified_track_record": getattr(mgr, "verified_track_record", "") or getattr(mgr, "management_experience", ""),
    }


def _build_factor_template_fallback(
    business_name: str,
    manager_name: str,
    factor_scores: Dict[str, float],
    overall_score: float,
    business_stage: str
) -> Dict[str, Any]:
    """Template-driven fallback based on highest and lowest factor scores."""
    sorted_factors = sorted(factor_scores.items(), key=lambda kv: kv[1], reverse=True)
    highest_factor, highest_score = sorted_factors[0] if sorted_factors else ("skills_fit", 80.0)
    lowest_factor, lowest_score = sorted_factors[-1] if sorted_factors else ("salary_fit", 60.0)

    factor_labels = {
        "industry_fit": "Industry Domain Fit",
        "skills_fit": "Core Skills Alignment",
        "experience_fit": "Depth of Experience",
        "leadership_fit": "Leadership & Team Management",
        "stage_fit": "Company Stage Compatibility",
        "salary_fit": "Compensation Budget Alignment",
    }
    high_label = factor_labels.get(highest_factor, highest_factor.replace("_", " ").title())
    low_label = factor_labels.get(lowest_factor, lowest_factor.replace("_", " ").title())

    return {
        "strengths": [
            f"Demonstrates exceptional alignment in {high_label} ({highest_score:.1f}/100), reinforcing strategic execution for {business_name}.",
            f"Strong overall profile compatibility ({overall_score:.1f}/100) across evaluated operational benchmarks."
        ],
        "concerns": [
            f"Primary operational trade-off is in {low_label} ({lowest_score:.1f}/100); requires structured onboarding calibration."
        ],
        "missing_requirements": [],
        "verdict": (
            f"{manager_name} presents a solid {overall_score:.1f}% operational match for {business_name}'s "
            f"{business_stage} trajectory, with {high_label.lower()} as a key execution asset."
        )
    }


@router.post("/calculate", response_model=BatchMatchResponse)
async def calculate_matches(
    req: CalculateMatchesRequest,
    include_explanations: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Calculate deterministic compatibility scores between a business and all candidate managers.
    Accepts either an existing 'business_id' OR an inline 'business_data' payload.
    Optional query param 'include_explanations=true' pre-computes explanations for the top 3 matches.
    """
    if not req.business_id and not req.business_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either 'business_id' or 'business_data'"
        )

    business_obj = None
    persisted_in_db = False

    # 1. Resolve business profile (prioritize dynamic business_data if provided)
    if req.business_data:
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
        db.add(business_obj)
        db.commit()
        db.refresh(business_obj)
        persisted_in_db = True
    elif req.business_id:
        biz_lookup_ids = [str(req.business_id)]
        if str(req.business_id) in ("biz-fashioncart", "biz_01"):
            biz_lookup_ids.extend(["biz-fashioncart", "biz_01"])
        result = db.execute(select(Business).filter(Business.id.in_(biz_lookup_ids)))
        business_obj = result.scalars().first()
        if not business_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business with ID '{req.business_id}' not found"
            )
        persisted_in_db = True

    # 2. Fetch all managers from the database
    mgr_result = db.execute(select(Manager))
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

    # 5. Batch pre-explanation optimization hook for top 3 candidates
    if include_explanations and matches_summary:
        biz_dict = _build_business_dict(business_obj)
        for idx in range(min(3, len(matches_summary))):
            cand_summary = matches_summary[idx]
            mgr_match = ranked[idx]
            mgr_dict = _build_manager_dict(mgr_match.manager)
            try:
                exp_res = await run_explainability_pipeline(
                    business=biz_dict,
                    manager=mgr_dict,
                    factor_scores=mgr_match.factor_scores,
                    overall_score=mgr_match.overall_score
                )
            except Exception:
                exp_res = _build_factor_template_fallback(
                    business_name=biz_dict["name"],
                    manager_name=mgr_dict["name"],
                    factor_scores=mgr_match.factor_scores,
                    overall_score=mgr_match.overall_score,
                    business_stage=biz_dict.get("stage", "Growth")
                )
            cand_summary.explanation = exp_res

    # 6. Persist top matches if business is stored in DB
    if persisted_in_db:
        for idx, r in enumerate(ranked[:10]):
            exp_data = matches_summary[idx].explanation if idx < len(matches_summary) and matches_summary[idx].explanation else None
            strengths = exp_data.get("strengths") if exp_data else None
            concerns = exp_data.get("concerns") if exp_data else None
            missing = exp_data.get("missing_requirements") if exp_data else None
            verdict = exp_data.get("verdict") if exp_data else None

            match_rec = MatchRecord(
                id=str(uuid.uuid4()),
                business_id=business_obj.id,
                manager_id=r.manager_id,
                overall_score=r.overall_score,
                factor_scores=r.factor_scores,
                strengths=strengths,
                weaknesses=concerns,
                risks=concerns,
                missing_requirements=missing,
                explanation=verdict,
                created_at=datetime.now(timezone.utc)
            )
            db.add(match_rec)
        db.commit()

    return BatchMatchResponse(
        business_id=business_obj.id,
        total_evaluated=len(all_managers),
        matches=matches_summary
    )


@router.get("/{business_id}", response_model=List[MatchRecordResponse])
def get_matches_for_business(
    business_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve historical match records for a business.
    """
    biz_result = db.execute(select(Business).filter(Business.id == business_id))
    biz = biz_result.scalars().first()
    if not biz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID '{business_id}' not found"
        )

    query = select(MatchRecord).filter(MatchRecord.business_id == business_id).order_by(MatchRecord.overall_score.desc())
    result = db.execute(query)
    records = result.scalars().all()
    return records


@router.post("/explain", response_model=ExplainMatchResponse)
async def explain_match(
    req: ExplainMatchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Generate explainable decision support card for a selected candidate.
    Accepts business_id, manager_id, and optional custom_business_context.
    Persists results to SQLite and returns full ExplainMatchResponse.
    """
    biz_id_str = str(req.business_id)
    mgr_id_str = str(req.manager_id)

    # 1. Fetch target Manager record from DB
    mgr_lookup_ids = [mgr_id_str]
    mgr_aliases = {
        "mgr_01": "mgr-sarah-khan",
        "mgr-sarah-khan": "mgr_01",
        "mgr_02": "mgr-maria-james",
        "mgr-maria-james": "mgr_02",
        "mgr_03": "mgr-ali-ahmed",
        "mgr-ali-ahmed": "mgr_03",
    }
    if mgr_id_str in mgr_aliases:
        mgr_lookup_ids.append(mgr_aliases[mgr_id_str])

    mgr_result = db.execute(select(Manager).filter(Manager.id.in_(mgr_lookup_ids)))
    mgr = mgr_result.scalars().first()
    if not mgr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manager with ID '{req.manager_id}' not found"
        )

    # 2. Fetch target Business record from DB or use incoming transient context
    biz_lookup_ids = [biz_id_str]
    if biz_id_str in ("biz-fashioncart", "biz_01"):
        biz_lookup_ids.extend(["biz-fashioncart", "biz_01"])
    biz_result = db.execute(select(Business).filter(Business.id.in_(biz_lookup_ids)))
    biz = biz_result.scalars().first()

    if not biz and not req.custom_business_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID '{req.business_id}' not found"
        )

    if not biz and req.custom_business_context:
        ctx = req.custom_business_context
        budget = ctx.get("salary_budget") or ctx.get("monthly_budget_usd", 0.0)
        challenges = ctx.get("challenges") or ctx.get("core_problem", "")
        goals = ctx.get("goals") or " ".join(ctx.get("primary_goals", []) or [])
        biz = Business(
            id=biz_id_str,
            name=ctx.get("name", "Custom Business"),
            industry=ctx.get("industry", "Technology"),
            size=ctx.get("size"),
            stage=ctx.get("stage", "Growth"),
            location=ctx.get("location"),
            employee_count=ctx.get("employee_count"),
            goals=goals,
            challenges=challenges,
            required_skills=ctx.get("required_skills", []),
            required_experience=ctx.get("required_experience", []),
            leadership_requirements=ctx.get("leadership_requirements"),
            salary_budget=float(budget or 0.0),
            work_arrangement=ctx.get("work_arrangement"),
        )
    elif biz and req.custom_business_context:
        ctx = req.custom_business_context
        if "industry" in ctx:
            biz.industry = ctx["industry"]
        if "stage" in ctx:
            biz.stage = ctx["stage"]
        if "goals" in ctx:
            biz.goals = ctx["goals"]
        if "challenges" in ctx:
            biz.challenges = ctx["challenges"]
        if "required_skills" in ctx:
            biz.required_skills = ctx["required_skills"]
        if "salary_budget" in ctx or "monthly_budget_usd" in ctx:
            biz.salary_budget = float(ctx.get("salary_budget") or ctx.get("monthly_budget_usd", 0.0))

    # 3. Deterministic calculation: strictly isolated and read-only
    match_result = calculate_match(biz, mgr)

    # 4. Context preparation
    biz_dict = _build_business_dict(biz)
    mgr_dict = _build_manager_dict(mgr)

    # 5. Execute LangGraph explainability pipeline with resilient error handling
    try:
        explanation_card = await run_explainability_pipeline(
            business=biz_dict,
            manager=mgr_dict,
            factor_scores=match_result.factor_scores,
            overall_score=match_result.overall_score
        )
    except Exception:
        explanation_card = _build_factor_template_fallback(
            business_name=biz_dict["name"],
            manager_name=mgr_dict["name"],
            factor_scores=match_result.factor_scores,
            overall_score=match_result.overall_score,
            business_stage=biz_dict.get("stage", "Growth")
        )

    # 6. Upsert or update corresponding MatchRecord in SQLite for auditability
    try:
        rec_query = select(MatchRecord).filter(
            MatchRecord.business_id == biz_id_str,
            MatchRecord.manager_id == mgr_id_str
        ).order_by(MatchRecord.created_at.desc())
        existing_rec = db.execute(rec_query).scalars().first()

        if existing_rec:
            existing_rec.overall_score = match_result.overall_score
            existing_rec.factor_scores = match_result.factor_scores
            existing_rec.strengths = explanation_card["strengths"]
            existing_rec.weaknesses = explanation_card["concerns"]
            existing_rec.risks = explanation_card["concerns"]
            existing_rec.missing_requirements = explanation_card.get("missing_requirements", [])
            existing_rec.explanation = explanation_card["verdict"]
        else:
            # Only create new DB record if business is persisted in businesses table
            biz_in_db = db.execute(select(Business).filter(Business.id == biz_id_str)).scalars().first()
            if biz_in_db:
                new_rec = MatchRecord(
                    id=str(uuid.uuid4()),
                    business_id=biz_id_str,
                    manager_id=mgr_id_str,
                    overall_score=match_result.overall_score,
                    factor_scores=match_result.factor_scores,
                    strengths=explanation_card["strengths"],
                    weaknesses=explanation_card["concerns"],
                    risks=explanation_card["concerns"],
                    missing_requirements=explanation_card.get("missing_requirements", []),
                    explanation=explanation_card["verdict"],
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_rec)
        db.commit()
    except Exception:
        db.rollback()

    # 7. Formulate and return ExplainMatchResponse
    mgr_title = getattr(mgr, "role_title", "") or getattr(mgr, "title", "Operations Manager")

    return ExplainMatchResponse(
        success=True,
        manager_id=req.manager_id,
        manager_name=mgr.name,
        manager_title=mgr_title,
        overall_score=match_result.overall_score,
        factor_scores=match_result.factor_scores,
        strengths=explanation_card["strengths"],
        concerns=explanation_card["concerns"],
        missing_requirements=explanation_card.get("missing_requirements", []),
        verdict=explanation_card["verdict"],
        generated_at=datetime.now(timezone.utc),
    )
