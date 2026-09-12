import os
import json
import asyncio
from app.core.database import engine, AsyncSessionLocal, Base
from app.models import Business, Manager

async def seed_database():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Loading seed data...")
    # Go up one directory to access the data/ folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    with open(os.path.join(data_dir, "sample_businesses.json"), "r", encoding="utf-8") as f:
        businesses_data = json.load(f)
        
    with open(os.path.join(data_dir, "sample_managers.json"), "r", encoding="utf-8") as f:
        managers_data = json.load(f)

    async with AsyncSessionLocal() as session:
        for b_data in businesses_data:
            # Map json fields to model
            biz = Business(
                id=b_data["id"],
                name=b_data["name"],
                industry=b_data["industry"],
                stage=b_data["stage"],
                monthly_budget_usd=b_data.get("monthly_budget_usd", 0),
                core_problem=b_data.get("core_problem", ""),
                primary_goals=b_data.get("primary_goals", []),
                required_skills=b_data.get("required_skills", []),
                raw_founder_notes=b_data.get("raw_founder_notes", "")
            )
            session.add(biz)
            
        for m_data in managers_data:
            mgr = Manager(
                id=m_data["id"],
                name=m_data["name"],
                role_title=m_data["role_title"],
                monthly_rate_usd=m_data.get("monthly_rate_usd", 0),
                verified_stages=m_data.get("verified_stages", []),
                industries=m_data.get("industries", []),
                core_skills=m_data.get("core_skills", []),
                years_experience=m_data.get("years_experience", 0),
                location=m_data.get("location", ""),
                verified_track_record=m_data.get("verified_track_record", ""),
                education=m_data.get("education", ""),
                availability=m_data.get("availability", "")
            )
            session.add(mgr)
            
        await session.commit()
    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_database())
