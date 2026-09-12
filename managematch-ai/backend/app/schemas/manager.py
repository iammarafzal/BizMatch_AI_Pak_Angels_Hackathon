from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ManagerBase(BaseModel):
    name: str
    role_title: str
    monthly_rate_usd: float
    verified_stages: List[str]
    industries: List[str]
    core_skills: List[str]
    years_experience: int
    location: str
    verified_track_record: str
    education: str
    availability: str

class ManagerCreate(ManagerBase):
    pass

class ManagerResponse(ManagerBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
