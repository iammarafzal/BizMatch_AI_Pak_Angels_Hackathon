import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, ForeignKey, Text, DateTime, JSON
from app.core.database import Base

class MatchRecord(Base):
    __tablename__ = "match_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String, ForeignKey("businesses.id"), nullable=False)
    manager_id = Column(String, ForeignKey("managers.id"), nullable=False)
    
    overall_score = Column(Float, nullable=False)
    factor_scores = Column(JSON, nullable=False, default=dict)
    
    strengths = Column(JSON, nullable=True, default=list)
    weaknesses = Column(JSON, nullable=True, default=list)
    risks = Column(JSON, nullable=True, default=list)
    missing_requirements = Column(JSON, nullable=True, default=list)
    
    explanation = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
