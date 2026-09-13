from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator

class BusinessBase(BaseModel):
    name: str
    industry: str
    size: Optional[str] = None
    stage: Optional[str] = None
    location: Optional[str] = None
    employee_count: Optional[int] = None
    business_model: Optional[str] = None
    goals: Optional[str] = None
    challenges: Optional[str] = None
    required_skills: Optional[List[str]] = []
    required_experience: Optional[List[str]] = []
    leadership_requirements: Optional[str] = None
    salary_budget: Optional[float] = 0.0
    work_arrangement: Optional[str] = None

    # Backward compatibility attributes (for legacy frontend/tests)
    monthly_budget_usd: Optional[float] = None
    core_problem: Optional[str] = None
    primary_goals: Optional[List[str]] = []
    raw_founder_notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_compat_fields(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            budget = getattr(data, "salary_budget", None)
            if budget is None:
                budget = getattr(data, "monthly_budget_usd", 0.0)
            challenges = getattr(data, "challenges", None) or getattr(data, "core_problem", "") or ""
            goals = getattr(data, "goals", None) or ""
            primary_goals = [goals] if goals else getattr(data, "primary_goals", [])
            skills = getattr(data, "required_skills", []) or []

            return {
                "id": getattr(data, "id", None),
                "name": getattr(data, "name", ""),
                "industry": getattr(data, "industry", ""),
                "size": getattr(data, "size", None),
                "stage": getattr(data, "stage", None),
                "location": getattr(data, "location", None),
                "employee_count": getattr(data, "employee_count", None),
                "business_model": getattr(data, "business_model", None),
                "goals": goals,
                "challenges": challenges,
                "required_skills": skills,
                "required_experience": getattr(data, "required_experience", []) or [],
                "leadership_requirements": getattr(data, "leadership_requirements", None),
                "salary_budget": float(budget or 0.0),
                "monthly_budget_usd": float(budget or 0.0),
                "core_problem": str(challenges),
                "primary_goals": primary_goals or [],
                "raw_founder_notes": str(challenges),
                "work_arrangement": getattr(data, "work_arrangement", None),
                "created_at": getattr(data, "created_at", None),
            }
        elif isinstance(data, dict):
            budget = data.get("salary_budget")
            if budget is None:
                budget = data.get("monthly_budget_usd", 0.0)
            challenges = data.get("challenges") or data.get("core_problem", "") or ""
            goals = data.get("goals") or ""
            primary_goals = [goals] if goals else data.get("primary_goals", [])

            data.setdefault("salary_budget", float(budget or 0.0))
            data.setdefault("monthly_budget_usd", float(budget or 0.0))
            data.setdefault("challenges", challenges)
            data.setdefault("core_problem", str(challenges))
            data.setdefault("goals", goals)
            data.setdefault("primary_goals", primary_goals)
            data.setdefault("raw_founder_notes", str(challenges))
            return data
        return data

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
