import uuid
import datetime
from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from app.core.database import Base
from app.models.business import JSONEncodedDict

class MatchRecord(Base):
    __tablename__ = "match_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id"), index=True)
    manager_id = Column(String, ForeignKey("managers.id"), index=True)
    
    # Deterministic scores
    overall_score = Column(Float, index=True)
    factor_scores = Column(JSONEncodedDict) # {industry: float, skills: float, stage: float, budget: float}
    
    # Gemini AI qualitative analysis
    qualitative_analysis = Column(JSONEncodedDict, nullable=True) # {strengths: [], concerns: [], missing_requirements: [], verdict: ""}
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
