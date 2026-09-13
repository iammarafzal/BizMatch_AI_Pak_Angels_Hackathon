import os
from sqlalchemy import text
from app.core.database import SessionLocal, engine, Base
from app.services.seeder import seed_database_if_empty
from app.models.manager import Manager
from app.models.business import Business
from app.models.match import MatchRecord

def reseed():
    db = SessionLocal()
    try:
        print("[RESEED] Clearing existing data tables...")
        db.query(MatchRecord).delete()
        db.query(Manager).delete()
        db.query(Business).delete()
        db.commit()
        print("[RESEED] Tables cleared. Seeding fresh dataset...")
        seed_database_if_empty(db)
        mgr_count = db.query(Manager).count()
        biz_count = db.query(Business).count()
        print(f"[RESEED SUCCESS] Seeded {mgr_count} managers and {biz_count} businesses.")
    except Exception as e:
        db.rollback()
        print(f"[RESEED ERROR] {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reseed()
