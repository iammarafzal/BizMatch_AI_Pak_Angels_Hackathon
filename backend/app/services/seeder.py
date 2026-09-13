import json
import os
import logging
from sqlalchemy.orm import Session
from app.models.manager import Manager
from app.models.business import Business
from app.models.user import User
from app.core.auth import hash_password
from app.core.database import SessionLocal

logger = logging.getLogger("bizmatch.seeder")

def seed_database_if_empty(db: Session = None):
    """
    Idempotent database seeder that populates SQLite with 16 managers,
    demo businesses, and default demo user credentials if the database is empty.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # 1. Check if already seeded
        manager_count = db.query(Manager).count()
        if manager_count > 0:
            logger.info(f"[SEED] Database already populated ({manager_count} managers). Skipping.")
            return

        logger.info("[SEED] Empty database detected. Seeding data from JSON fixtures...")

        # 2. Locate managers.json
        possible_managers_paths = [
            os.path.join(os.path.dirname(__file__), "../data/managers.json"),
            os.path.join(os.path.dirname(__file__), "../../data/managers.json"),
            os.path.join(os.getcwd(), "data", "managers.json"),
            os.path.join(os.getcwd(), "backend", "data", "managers.json"),
            "data/managers.json",
            "backend/data/managers.json",
        ]
        managers_path = None
        for p in possible_managers_paths:
            normalized = os.path.abspath(p)
            if os.path.isfile(normalized):
                managers_path = normalized
                break

        if not managers_path:
            raise FileNotFoundError("managers.json fixture could not be located in any known data directory.")

        with open(managers_path, "r", encoding="utf-8") as f:
            managers_data = json.load(f)
            for m in managers_data:
                manager_obj = Manager(
                    id=m["id"],
                    name=m["name"],
                    title=m["title"],
                    years_experience=m["years_experience"],
                    industries=m["industries"],
                    skills=m["skills"],
                    previous_roles=m["previous_roles"],
                    management_experience=m["management_experience"],
                    leadership_score=m["leadership_score"],
                    achievements=m["achievements"],
                    salary_expectation=m["salary_expectation"],
                    availability=m["availability"],
                    location=m["location"],
                    work_preference=m["work_preference"]
                )
                db.add(manager_obj)

        # 3. Locate and load demo businesses
        possible_biz_paths = [
            os.path.join(os.path.dirname(__file__), "../data/businesses.json"),
            os.path.join(os.path.dirname(__file__), "../../data/businesses.json"),
            os.path.join(os.getcwd(), "data", "businesses.json"),
            os.path.join(os.getcwd(), "backend", "data", "businesses.json"),
            "data/businesses.json",
            "backend/data/businesses.json",
        ]
        businesses_path = None
        for p in possible_biz_paths:
            normalized = os.path.abspath(p)
            if os.path.isfile(normalized):
                businesses_path = normalized
                break

        if businesses_path and os.path.isfile(businesses_path):
            with open(businesses_path, "r", encoding="utf-8") as f:
                businesses_data = json.load(f)
                for b in businesses_data:
                    business_obj = Business(
                        id=b["id"],
                        name=b["name"],
                        industry=b["industry"],
                        size=b.get("size", "Small"),
                        stage=b.get("stage", "Growth"),
                        employee_count=b.get("employee_count", 12),
                        business_model=b.get("business_model", "Online retail / Direct-to-Consumer"),
                        location=b.get("location", "Lahore, Pakistan"),
                        salary_budget=b["salary_budget"],
                        work_arrangement=b.get("work_arrangement", "Hybrid"),
                        goals=b["goals"],
                        challenges=b["challenges"],
                        required_skills=b["required_skills"],
                        required_experience=b.get("required_experience", []),
                        leadership_requirements=b.get("leadership_requirements", "")
                    )
                    db.add(business_obj)

        # 4. Ensure default demo user exists for seamless JWT token acquisition
        demo_user = db.query(User).filter(User.email == "founder@bizmatch.ai").first()
        if not demo_user:
            demo_user = User(
                email="founder@bizmatch.ai",
                hashed_password=hash_password("password123"),
                full_name="Demo Founder",
                role="founder"
            )
            db.add(demo_user)

        db.commit()
        logger.info(f"[SEED] Successfully seeded {len(managers_data)} managers and demo scenarios into SQLite.")
        print(f"[SEED] Successfully seeded {len(managers_data)} managers into SQLite.")
    except Exception as e:
        db.rollback()
        logger.error(f"[SEED ERROR] Failed to seed database: {e}")
        print(f"[SEED ERROR] Failed to seed database: {e}")
        raise
    finally:
        if close_session:
            db.close()
