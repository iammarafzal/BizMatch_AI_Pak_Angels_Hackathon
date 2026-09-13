import os
import sys
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.core.database import SessionLocal
from app.models.match import MatchRecord


async def get_auth_headers(client: AsyncClient):
    login_res = await client.post("/api/auth/login", json={"email": "founder@bizmatch.ai", "password": "password123"})
    if login_res.status_code == 200:
        token = login_res.json().get("access_token")
        if token:
            return {"Authorization": f"Bearer {token}"}
    return {}


async def test_explain_endpoint_sarah_khan():
    """Verify POST /api/matches/explain returns complete decision support card."""
    print("\n--- 1. Testing POST /api/matches/explain (Sarah Khan & FashionCart) ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = await get_auth_headers(client)
        payload = {
            "business_id": "biz-fashioncart",
            "manager_id": "mgr-sarah-khan"
        }
        res = await client.post("/api/matches/explain", json=payload, headers=headers)
        assert res.status_code == 200, f"Explain endpoint failed: {res.text}"
        
        data = res.json()
        assert data["success"] is True
        assert data["manager_id"] == "mgr-sarah-khan"
        assert data["manager_name"] == "Sarah Khan"
        assert len(data["manager_title"]) > 0
        assert 90.0 <= data["overall_score"] <= 95.0
        assert data["overall_score"] == 92.8
        
        factors = data["factor_scores"]
        expected_factors = ["industry_fit", "skills_fit", "experience_fit", "leadership_fit", "stage_fit", "salary_fit"]
        for ef in expected_factors:
            assert ef in factors, f"Missing factor {ef}"
            assert 0.0 <= factors[ef] <= 100.0

        assert 2 <= len(data["strengths"]) <= 4
        assert 1 <= len(data["concerns"]) <= 3
        assert isinstance(data["missing_requirements"], list)
        assert len(data["verdict"]) > 15
        assert "generated_at" in data

        # Verify envelope compatibility
        assert "data" in data
        assert data["data"]["verdict"] == data["verdict"]

        print(f"[PASS] Retrieved decision card for {data['manager_name']} ({data['overall_score']}%)")
        print(f"       Strengths: {data['strengths']}")
        print(f"       Concerns: {data['concerns']}")
        print(f"       Verdict: {data['verdict']}")


async def test_database_persistence_of_explanation():
    """Verify that MatchRecord in SQLite persists explanation, strengths, weaknesses, and risks."""
    print("\n--- 2. Testing MatchRecord Database Upsert & Persistence ---")
    with SessionLocal() as session:
        query = select(MatchRecord).filter(
            MatchRecord.business_id == "biz-fashioncart",
            MatchRecord.manager_id == "mgr-sarah-khan"
        ).order_by(MatchRecord.created_at.desc())
        
        result = session.execute(query)
        rec = result.scalars().first()
        
        assert rec is not None, "MatchRecord was not persisted in PostgreSQL database"
        assert 90.0 <= rec.overall_score <= 95.0
        assert isinstance(rec.factor_scores, dict)
        assert isinstance(rec.strengths, list) and len(rec.strengths) >= 2
        assert isinstance(rec.weaknesses, list) and len(rec.weaknesses) >= 1
        assert isinstance(rec.risks, list) and len(rec.risks) >= 1
        assert rec.explanation is not None and len(rec.explanation) > 10
        print(f"[PASS] MatchRecord verified in DB with ID: {rec.id}")
        print(f"       DB Strengths: {len(rec.strengths)} items | DB Weaknesses/Risks: {len(rec.weaknesses)} items")


async def test_explain_endpoint_404_handling():
    """Verify clean 404 responses for invalid business or manager IDs."""
    print("\n--- 3. Testing 404 Not Found Handling ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = await get_auth_headers(client)
        # Invalid business_id
        res_bad_biz = await client.post("/api/matches/explain", json={
            "business_id": "biz-non-existent",
            "manager_id": "mgr-sarah-khan"
        }, headers=headers)
        assert res_bad_biz.status_code == 404, f"Expected 404 for bad business, got {res_bad_biz.status_code}"
        assert "not found" in res_bad_biz.json()["detail"].lower()
        print("[PASS] 404 correctly returned for non-existent business_id.")

        # Invalid manager_id
        res_bad_mgr = await client.post("/api/matches/explain", json={
            "business_id": "biz-fashioncart",
            "manager_id": "mgr-non-existent"
        }, headers=headers)
        assert res_bad_mgr.status_code == 404, f"Expected 404 for bad manager, got {res_bad_mgr.status_code}"
        assert "not found" in res_bad_mgr.json()["detail"].lower()
        print("[PASS] 404 correctly returned for non-existent manager_id.")


async def test_custom_business_context_evaluation():
    """Verify on-the-fly evaluation using transient custom_business_context."""
    print("\n--- 4. Testing Transient custom_business_context ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = await get_auth_headers(client)
        payload = {
            "business_id": "transient-custom-biz",
            "manager_id": "mgr-sarah-khan",
            "custom_business_context": {
                "name": "QuickMart Express",
                "industry": "E-Commerce Logistics",
                "stage": "Growth",
                "salary_budget": 2500.0,
                "goals": "Automate fulfillment hubs across 3 cities.",
                "challenges": "Last-mile dispatch bottlenecks and team coordination issues.",
                "required_skills": ["Operations Management", "Supply Chain", "Process Optimization"]
            }
        }
        res = await client.post("/api/matches/explain", json=payload, headers=headers)
        assert res.status_code == 200, f"Custom context evaluation failed: {res.text}"
        data = res.json()
        assert data["success"] is True
        assert data["overall_score"] > 85.0
        assert len(data["strengths"]) >= 2
        print(f"[PASS] Successfully evaluated transient business context for {data['manager_name']}.")


async def test_batch_matches_with_include_explanations():
    """Verify include_explanations=true parameter pre-computes explanations for top 3 candidates."""
    print("\n--- 5. Testing POST /api/matches/calculate?include_explanations=true ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = await get_auth_headers(client)
        res = await client.post(
            "/api/matches/calculate?include_explanations=true",
            json={"business_id": "biz-fashioncart"},
            headers=headers
        )
        assert res.status_code == 200, f"Calculate with explanations failed: {res.text}"
        batch = res.json()
        matches = batch["matches"]
        assert len(matches) >= 3

        # Top 3 candidates must have explanation populated
        for i in range(3):
            match_item = matches[i]
            assert match_item["explanation"] is not None, f"Match #{i+1} missing pre-computed explanation"
            exp = match_item["explanation"]
            assert "strengths" in exp and len(exp["strengths"]) >= 2
            assert "concerns" in exp and len(exp["concerns"]) >= 1
            assert "verdict" in exp and len(exp["verdict"]) > 10
            print(f"[PASS] Pre-computed explanation verified for top candidate #{i+1}: {match_item['manager']['name']}")

        # Candidates past top 3 should not have pre-computed explanations
        if len(matches) > 3:
            assert matches[3]["explanation"] is None
            print("[PASS] Matches past index 3 have explanation=None as expected for optimization.")


async def test_v1_prefix_route():
    """Verify endpoint is accessible under /api/v1 prefix as well."""
    print("\n--- 6. Testing /api/v1/matches/explain Prefix Route ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = await get_auth_headers(client)
        res = await client.post("/api/v1/matches/explain", json={
            "business_id": "biz-fashioncart",
            "manager_id": "mgr-sarah-khan"
        }, headers=headers)
        assert res.status_code == 200
        assert res.json()["success"] is True
        print("[PASS] /api/v1/matches/explain confirmed functional.")


async def main():
    await test_explain_endpoint_sarah_khan()
    await test_database_persistence_of_explanation()
    await test_explain_endpoint_404_handling()
    await test_custom_business_context_evaluation()
    await test_batch_matches_with_include_explanations()
    await test_v1_prefix_route()
    print("\n=======================================================")
    print("ALL TASK 8 EXPLANATION API TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")


if __name__ == "__main__":
    asyncio.run(main())
