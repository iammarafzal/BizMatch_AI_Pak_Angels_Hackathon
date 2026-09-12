import uuid
import json
from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.types import TypeDecorator, TEXT
from app.core.database import Base

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class JSONEncodedList(TypeDecorator):
    """Represents an immutable list as a json-encoded string."""
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)
    industry = Column(String)
    stage = Column(String)
    monthly_budget_usd = Column(Float)
    core_problem = Column(String)
    primary_goals = Column(JSONEncodedList)
    required_skills = Column(JSONEncodedList)
    raw_founder_notes = Column(String)
