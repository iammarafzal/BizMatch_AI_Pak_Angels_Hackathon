from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator

class ManagerBase(BaseModel):
    name: str
    title: str
    years_experience: Optional[float] = 0.0
    industries: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    previous_roles: Optional[List[str]] = []
    management_experience: Optional[str] = None
    leadership_score: Optional[float] = 0.0
    achievements: Optional[List[str]] = []
    salary_expectation: Optional[float] = 0.0
    availability: Optional[str] = None
    location: Optional[str] = None
    work_preference: Optional[str] = None

    # Backward compatibility fields (for legacy frontend/tests)
    role_title: Optional[str] = None
    monthly_rate_usd: Optional[float] = None
    verified_stages: Optional[List[str]] = []
    core_skills: Optional[List[str]] = []
    verified_track_record: Optional[str] = None
    education: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_compat_fields(cls, data: Any) -> Any:
        if hasattr(data, "__dict__"):
            title = getattr(data, "title", None) or getattr(data, "role_title", None) or ""
            salary = getattr(data, "salary_expectation", None)
            if salary is None:
                salary = getattr(data, "monthly_rate_usd", 0.0)
            skills = getattr(data, "skills", None) or getattr(data, "core_skills", None) or []
            achievements = getattr(data, "achievements", None) or []
            track_record = getattr(data, "management_experience", None) or (achievements[0] if achievements else "")

            return {
                "id": getattr(data, "id", None),
                "name": getattr(data, "name", ""),
                "title": title,
                "role_title": title,
                "years_experience": float(getattr(data, "years_experience", 0.0) or 0.0),
                "industries": getattr(data, "industries", []) or [],
                "skills": skills,
                "core_skills": skills,
                "previous_roles": getattr(data, "previous_roles", []) or [],
                "management_experience": getattr(data, "management_experience", None),
                "leadership_score": float(getattr(data, "leadership_score", 0.0) or 0.0),
                "achievements": achievements,
                "salary_expectation": float(salary or 0.0),
                "monthly_rate_usd": float(salary or 0.0),
                "availability": getattr(data, "availability", None),
                "location": getattr(data, "location", None),
                "work_preference": getattr(data, "work_preference", None),
                "verified_stages": getattr(data, "industries", []) or [],
                "verified_track_record": str(track_record or ""),
                "education": "Verified Professional",
                "created_at": getattr(data, "created_at", None),
            }
        elif isinstance(data, dict):
            title = data.get("title") or data.get("role_title") or ""
            salary = data.get("salary_expectation")
            if salary is None:
                salary = data.get("monthly_rate_usd", 0.0)
            skills = data.get("skills") or data.get("core_skills") or []
            achievements = data.get("achievements") or []
            track_record = data.get("management_experience") or (achievements[0] if achievements else "")

            data.setdefault("title", title)
            data.setdefault("role_title", title)
            data.setdefault("salary_expectation", float(salary or 0.0))
            data.setdefault("monthly_rate_usd", float(salary or 0.0))
            data.setdefault("skills", skills)
            data.setdefault("core_skills", skills)
            data.setdefault("verified_track_record", str(track_record or ""))
            data.setdefault("education", "Verified Professional")
            data.setdefault("verified_stages", data.get("industries", []))
            return data
        return data

class ManagerCreate(ManagerBase):
    pass

class ManagerResponse(ManagerBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
