from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Optional
from datetime import datetime

class FactorScores(BaseModel):
    industry: float
    skills: float
    stage: float
    budget: float

class QualitativeAnalysis(BaseModel):
    strengths: List[str]
    concerns: List[str]
    missing_requirements: List[str]
    verdict: str

class MatchRecordBase(BaseModel):
    business_id: str
    manager_id: str
    overall_score: float
    factor_scores: FactorScores
    qualitative_analysis: Optional[QualitativeAnalysis] = None

class MatchRecordCreate(MatchRecordBase):
    pass

class MatchRecordResponse(MatchRecordBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AnalyzeRequirementsRequest(BaseModel):
    goals: str
    challenges: str
    raw_preferences: str

class AnalyzeRequirementsResponse(BaseModel):
    success: bool
    data: dict

class CalculateMatchesRequest(BaseModel):
    business_id: str

class CalculateMatchesResponse(BaseModel):
    success: bool
    data: List[MatchRecordResponse]

class ExplainMatchRequest(BaseModel):
    business_id: str
    manager_id: str

class ExplainMatchResponse(BaseModel):
    success: bool
    data: QualitativeAnalysis
