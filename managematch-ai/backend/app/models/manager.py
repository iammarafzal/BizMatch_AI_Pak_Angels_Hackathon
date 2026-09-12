import uuid
from sqlalchemy import Column, String, Float, Integer
from app.core.database import Base
from app.models.business import JSONEncodedList

class Manager(Base):
    __tablename__ = "managers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    role_title = Column(String)
    monthly_rate_usd = Column(Float)
    verified_stages = Column(JSONEncodedList)
    industries = Column(JSONEncodedList)
    core_skills = Column(JSONEncodedList)
    years_experience = Column(Integer)
    location = Column(String)
    verified_track_record = Column(String)
    education = Column(String)
    availability = Column(String)
