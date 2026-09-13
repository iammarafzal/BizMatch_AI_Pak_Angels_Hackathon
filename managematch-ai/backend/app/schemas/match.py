from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from app.schemas.manager import ManagerResponse
from app.schemas.business import BusinessCreate

class MatchFactorScores(BaseModel):
    industry_fit: float
    skills_fit: float
    experience_fit: float
    leadership_fit: float
    stage_fit: float
    salary_fit: float

    model_config = ConfigDict(extra="ignore")

class CandidateMatchSummary(BaseModel):
    manager: ManagerResponse
    overall_score: float
    factor_scores: MatchFactorScores

class BatchMatchResponse(BaseModel):
    business_id: str
    total_evaluated: int
    matches: List[CandidateMatchSummary]

class CalculateMatchesRequest(BaseModel):
    business_id: Optional[str] = None
    business_data: Optional[BusinessCreate] = None

class FactorScores(BaseModel):
    industry: Optional[float] = None
    skills: Optional[float] = None
    stage: Optional[float] = None
    budget: Optional[float] = None
    industry_fit: Optional[float] = None
    skills_fit: Optional[float] = None
    experience_fit: Optional[float] = None
    leadership_fit: Optional[float] = None
    stage_fit: Optional[float] = None
    salary_fit: Optional[float] = None

    model_config = ConfigDict(extra="allow")

class QualitativeAnalysis(BaseModel):
    strengths: List[str]
    concerns: List[str]
    missing_requirements: List[str]
    verdict: str

class MatchRecordBase(BaseModel):
    business_id: str
    manager_id: str
    overall_score: float
    factor_scores: Union[FactorScores, Dict[str, Any]]
    qualitative_analysis: Optional[QualitativeAnalysis] = None

class MatchRecordCreate(MatchRecordBase):
    pass

class MatchRecordResponse(MatchRecordBase):
    id: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AnalyzeRequirementsRequest(BaseModel):
    goals: str
    challenges: str
    raw_preferences: str

class AnalyzeRequirementsResponse(BaseModel):
    success: bool
    data: dict

class CalculateMatchesResponse(BaseModel):
    success: bool
    data: List[MatchRecordResponse]

class ExplainMatchRequest(BaseModel):
    business_id: str
    manager_id: str

class ExplainMatchResponse(BaseModel):
    success: bool
    data: QualitativeAnalysis
