from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from app.schemas.manager import ManagerResponse
from app.schemas.business import BusinessCreate

class StructuredRequirements(BaseModel):
    industry: str = Field(description="Normalized industry or business vertical (e.g., fashion e-commerce, b2b saas)")
    business_stage: str = Field(description="Inferred or stated business stage (e.g., Early, Growth, Scaling)")
    key_priorities: List[str] = Field(description="Top 3-4 operational, strategic, or scaling priorities")
    required_skills: List[str] = Field(description="Standardized technical and management skills needed")
    experience_requirements: List[str] = Field(description="Domain-specific and leadership experience requirements")
    experience_profile: Optional[List[str]] = None

    model_config = ConfigDict(extra="ignore")

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
    missing_requirements: List[str] = Field(default_factory=list)
    verdict: str
    manager_id: Optional[str] = None
    overall_score: Optional[float] = None
    factor_scores: Optional[Dict[str, float]] = None

    model_config = ConfigDict(extra="allow")

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
    name: Optional[str] = None
    industry: Optional[str] = None
    stage: Optional[str] = None
    goals: str
    challenges: str
    raw_preferences: Optional[str] = None

class AnalyzeRequirementsResponse(BaseModel):
    success: bool
    data: Union[StructuredRequirements, dict]

class CalculateMatchesResponse(BaseModel):
    success: bool
    data: List[MatchRecordResponse]

class ExplainMatchRequest(BaseModel):
    business_id: str
    manager_id: str

class ExplainMatchResponse(BaseModel):
    success: bool
    data: Union[QualitativeAnalysis, Dict[str, Any]]
