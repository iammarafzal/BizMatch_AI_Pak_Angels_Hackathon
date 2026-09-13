from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/demo", tags=["Demo"])

FASHIONCART_DEMO_SCENARIO: Dict[str, Any] = {
    "id": "biz-fashioncart",
    "business_id": "biz-fashioncart",
    "name": "FashionCart",
    "industry": "Fashion E-commerce",
    "size": "Small",
    "stage": "Growth",
    "employee_count": 12,
    "budget": 2000.0,
    "salary_budget": 2000.0,
    "monthly_budget_usd": 2000.0,
    "location": "Lahore / Hybrid",
    "work_arrangement": "Remote/Hybrid",
    "goals": "We want to double our revenue within the next 12 months and expand our operations.",
    "challenges": "Our orders have increased significantly, but our fulfillment process is disorganized and our employees don't have clearly defined responsibilities.",
    "core_problem": "Our orders have increased significantly, but our fulfillment process is disorganized and our employees don't have clearly defined responsibilities.",
    "primary_goals": [
        "Double revenue within the next 12 months and expand operations",
        "Reorganize order fulfillment workflows and eliminate delivery bottlenecks",
        "Establish clearly defined employee responsibilities and standard operating procedures (SOPs)"
    ],
    "required_skills": [
        "Operations Management",
        "Process Optimization",
        "Team Management",
        "Supply Chain"
    ],
    "required_experience": [
        "E-commerce operations",
        "Warehouse inventory management",
        "Team leadership"
    ]
}

@router.get("/fashioncart")
async def get_fashioncart_demo_preset() -> Dict[str, Any]:
    """
    Returns the pre-configured FashionCart test scenario payload.
    Used by the frontend '⚡ Load FashionCart Demo' preset button to instantly
    hydrate onboarding wizard forms in under one second.
    """
    return {
        "success": True,
        "data": FASHIONCART_DEMO_SCENARIO,
        **FASHIONCART_DEMO_SCENARIO
    }
