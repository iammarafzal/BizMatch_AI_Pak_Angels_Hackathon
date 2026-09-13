from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.models.business import Business

router = APIRouter(prefix="/demo", tags=["Demo"])

FASHIONCART_FALLBACK_SCENARIO: Dict[str, Any] = {
    "id": "biz-fashioncart",
    "business_id": "biz-fashioncart",
    "name": "FashionCart",
    "industry": "Fashion E-commerce",
    "size": "Small",
    "stage": "Growth",
    "employee_count": 12,
    "business_model": "Online Retail",
    "salary_budget": 2000.0,
    "budget": 2000.0,
    "monthly_budget_usd": 2000.0,
    "work_arrangement": "Hybrid",
    "location": "Lahore, Pakistan",
    "goals": "We want to double our revenue within the next 12 months and expand regional distribution.",
    "challenges": "Our orders have increased significantly, but fulfillment is disorganized, stock counts are inconsistent, and staff lack defined roles.",
    "core_problem": "Our orders have increased significantly, but fulfillment is disorganized, stock counts are inconsistent, and staff lack defined roles.",
    "required_skills": [
        "Operations Management",
        "Process Optimization",
        "Team Leadership",
        "E-commerce Logistics"
    ],
    "required_experience": [
        "Scaling operations",
        "Team structure setup",
        "Inventory systems"
    ],
    "leadership_requirements": "Must possess strong team leadership to reorganize a 12-person operations team and establish clear accountability and standard operating procedures (SOPs)."
}

@router.get("/fashioncart")
def get_fashioncart_demo_preset(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns the pre-configured FashionCart test scenario payload from the database.
    Used by the frontend '⚡ Load FashionCart Demo' preset button to instantly
    hydrate onboarding wizard forms directly from live backend records.
    """
    # Query database for seeded FashionCart business
    stmt = select(Business).filter(
        (Business.id == "biz-fashioncart") | 
        (Business.id == "biz_01") | 
        (Business.name.ilike("%fashioncart%"))
    )
    biz = db.execute(stmt).scalars().first()

    if biz:
        scenario = {
            "id": biz.id,
            "business_id": biz.id,
            "name": biz.name,
            "industry": biz.industry,
            "size": biz.size or "Small",
            "stage": biz.stage or "Growth",
            "employee_count": biz.employee_count or 12,
            "business_model": biz.business_model or "Online Retail",
            "salary_budget": float(biz.salary_budget or 2000.0),
            "budget": float(biz.salary_budget or 2000.0),
            "monthly_budget_usd": float(biz.salary_budget or 2000.0),
            "location": biz.location or "Lahore, Pakistan",
            "work_arrangement": biz.work_arrangement or "Hybrid",
            "goals": biz.goals or "We want to double our revenue within the next 12 months and expand regional distribution.",
            "challenges": biz.challenges or "Our orders have increased significantly, but fulfillment is disorganized, stock counts are inconsistent, and staff lack defined roles.",
            "core_problem": biz.challenges or "Our orders have increased significantly, but fulfillment is disorganized, stock counts are inconsistent, and staff lack defined roles.",
            "required_skills": biz.required_skills or [
                "Operations Management",
                "Process Optimization",
                "Team Leadership",
                "E-commerce Logistics"
            ],
            "required_experience": biz.required_experience or [
                "Scaling operations",
                "Team structure setup",
                "Inventory systems"
            ],
            "leadership_requirements": biz.leadership_requirements or "Must possess strong team leadership to reorganize a 12-person operations team."
        }
    else:
        scenario = FASHIONCART_FALLBACK_SCENARIO

    return {
        "success": True,
        "data": scenario,
        **scenario
    }
