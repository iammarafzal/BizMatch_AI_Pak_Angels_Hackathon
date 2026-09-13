import os
import sys
import json
import asyncio
import argparse
from typing import Dict, Any, Tuple
from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal, Base
from app.models.business import Business
from app.models.manager import Manager
# Import MatchRecord so its metadata is registered on Base as well
from app.models.match import MatchRecord

def find_fixture_path(filename: str) -> str:
    """Find fixture file in backend/data or root data directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(current_dir, "..", "..", "data", filename),
        os.path.join(current_dir, "..", "..", "..", "data", filename),
        os.path.join(os.getcwd(), "data", filename),
        os.path.join(os.getcwd(), "backend", "data", filename),
    ]
    for path in candidates:
        normalized = os.path.abspath(path)
        if os.path.isfile(normalized):
            return normalized
    raise FileNotFoundError(f"Fixture file '{filename}' could not be located in any known data directory.")

async def seed_database(reset: bool = False) -> Dict[str, Any]:
    """
    Seed the PostgreSQL database with managers and businesses fixtures.
    Idempotent: skips records that already exist by ID.
    If reset=True, drops and recreates all tables before seeding.
    """
    async with engine.begin() as conn:
        if reset:
            print("[INFO] Reset mode active: dropping all existing database tables...")
            await conn.run_sync(Base.metadata.drop_all)
        # Ensure tables exist
        await conn.run_sync(Base.metadata.create_all)

    managers_path = find_fixture_path("managers.json")
    businesses_path = find_fixture_path("businesses.json")

    with open(managers_path, "r", encoding="utf-8") as f:
        managers_data = json.load(f)

    with open(businesses_path, "r", encoding="utf-8") as f:
        businesses_data = json.load(f)

    seeded_managers = 0
    skipped_managers = 0
    seeded_businesses = 0
    skipped_businesses = 0

    async with AsyncSessionLocal() as session:
        # Check existing businesses
        biz_result = await session.execute(select(Business.id))
        existing_biz_ids = set(biz_result.scalars().all())

        for b_data in businesses_data:
            biz_id = b_data.get("id")
            if biz_id in existing_biz_ids:
                skipped_businesses += 1
                continue

            business = Business(
                id=biz_id,
                name=b_data["name"],
                industry=b_data["industry"],
                size=b_data.get("size"),
                stage=b_data.get("stage"),
                location=b_data.get("location"),
                employee_count=b_data.get("employee_count"),
                business_model=b_data.get("business_model"),
                goals=b_data.get("goals"),
                challenges=b_data.get("challenges"),
                required_skills=b_data.get("required_skills", []),
                required_experience=b_data.get("required_experience", []),
                leadership_requirements=b_data.get("leadership_requirements"),
                salary_budget=float(b_data["salary_budget"]) if "salary_budget" in b_data else None,
                work_arrangement=b_data.get("work_arrangement"),
            )
            session.add(business)
            existing_biz_ids.add(biz_id)
            seeded_businesses += 1

        # Check existing managers
        mgr_result = await session.execute(select(Manager.id))
        existing_mgr_ids = set(mgr_result.scalars().all())

        for m_data in managers_data:
            mgr_id = m_data.get("id")
            if mgr_id in existing_mgr_ids:
                skipped_managers += 1
                continue

            manager = Manager(
                id=mgr_id,
                name=m_data["name"],
                title=m_data["title"],
                years_experience=float(m_data["years_experience"]) if "years_experience" in m_data else None,
                industries=m_data.get("industries", []),
                skills=m_data.get("skills", []),
                previous_roles=m_data.get("previous_roles", []),
                management_experience=m_data.get("management_experience"),
                leadership_score=float(m_data["leadership_score"]) if "leadership_score" in m_data else None,
                achievements=m_data.get("achievements", []),
                salary_expectation=float(m_data["salary_expectation"]) if "salary_expectation" in m_data else None,
                availability=m_data.get("availability"),
                location=m_data.get("location"),
                work_preference=m_data.get("work_preference"),
            )
            session.add(manager)
            existing_mgr_ids.add(mgr_id)
            seeded_managers += 1

        await session.commit()

    total_businesses = seeded_businesses + skipped_businesses
    total_managers = seeded_managers + skipped_managers

    summary_msg = (
        f"Successfully seeded {seeded_managers} managers and {seeded_businesses} businesses "
        f"(Total in DB: {total_managers} managers, {total_businesses} businesses; "
        f"Skipped existing: {skipped_managers} managers, {skipped_businesses} businesses)."
    )
    print(f"[SUCCESS] {summary_msg}")

    return {
        "seeded_managers": seeded_managers,
        "skipped_managers": skipped_managers,
        "total_managers": total_managers,
        "seeded_businesses": seeded_businesses,
        "skipped_businesses": skipped_businesses,
        "total_businesses": total_businesses,
        "reset": reset,
    }

def main():
    parser = argparse.ArgumentParser(description="BizMatch AI Database Seeder")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate all database tables before seeding fixtures."
    )
    args = parser.parse_args()
    asyncio.run(seed_database(reset=args.reset))

if __name__ == "__main__":
    main()
