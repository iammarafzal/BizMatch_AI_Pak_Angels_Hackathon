from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class BusinessBase(BaseModel):
    name: str
    industry: str
    stage: str
    monthly_budget_usd: float
    core_problem: str
    primary_goals: List[str]
    required_skills: List[str]
    raw_founder_notes: Optional[str] = None

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
