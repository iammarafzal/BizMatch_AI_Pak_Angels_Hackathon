import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON
from app.core.database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    industry = Column(String, nullable=False)
    size = Column(String, nullable=True)
    stage = Column(String, nullable=True)
    location = Column(String, nullable=True)
    employee_count = Column(Integer, nullable=True)
    business_model = Column(String, nullable=True)
    
    goals = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)
    
    required_skills = Column(JSON, nullable=True)
    required_experience = Column(JSON, nullable=True)
    leadership_requirements = Column(Text, nullable=True)
    
    salary_budget = Column(Float, nullable=True)
    work_arrangement = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
