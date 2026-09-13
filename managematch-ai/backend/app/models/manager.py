import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Text, DateTime, JSON
from app.core.database import Base

class Manager(Base):
    __tablename__ = "managers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    
    years_experience = Column(Float, nullable=True)
    industries = Column(JSON, nullable=True)
    skills = Column(JSON, nullable=True)
    previous_roles = Column(JSON, nullable=True)
    
    management_experience = Column(Text, nullable=True)
    leadership_score = Column(Float, nullable=True)
    achievements = Column(JSON, nullable=True)
    
    salary_expectation = Column(Float, nullable=True)
    availability = Column(String, nullable=True)
    location = Column(String, nullable=True)
    work_preference = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
