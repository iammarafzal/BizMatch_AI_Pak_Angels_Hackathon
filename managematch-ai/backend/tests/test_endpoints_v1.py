import os
import sys
import asyncio
from httpx import AsyncClient, ASGITransport

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

async def test_task5_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n=== RUNNING TASK 5: CORE CRUD & MATCHING ENDPOINTS TEST SUITE ===")

        # -------------------------------------------------------------
        # 1. Business Endpoints
        # -------------------------------------------------------------
        print("\n--- 1. Testing Business Endpoints ---")
        # 1.1 POST /api/businesses (Create new business)
        new_biz_payload = {
            "name": "NovaLogix Solutions",
            "industry": "Logistics",
            "size": "Seed",
            "stage": "Seed",
            "location": "Lahore, Pakistan",
            "employee_count": 9,
            "business_model": "Freight Tech",
            "goals": "Automate dispatch routes and reduce delivery turnaround by 30%.",
            "challenges": "Manual routing errors causing customer churn and excess fuel cost.",
            "required_skills": ["Fleet Dispatch", "Route Optimization", "Supply Chain Optimization"],
            "required_experience": ["Logistics fleet management", "Route planning"],
            "leadership_requirements": "Hands-on logistics operations lead.",
            "salary_budget": 2100.0,
            "work_arrangement": "Hybrid"
        }
        res = await client.post("/api/businesses/", json=new_biz_payload)
        assert res.status_code == 201, f"POST /api/businesses failed: {res.text}"
        created_biz = res.json()
        assert created_biz["name"] == "NovaLogix Solutions"
        assert created_biz["salary_budget"] == 2100.0
        created_biz_id = created_biz["id"]
        print(f"[PASS] POST /api/businesses -> Created business '{created_biz['name']}' (ID: {created_biz_id}) with 201 Created.")

        # 1.2 GET /api/businesses (List businesses)
        res = await client.get("/api/businesses/")
        assert res.status_code == 200, f"GET /api/businesses failed: {res.text}"
        biz_list = res.json()
        assert len(biz_list) >= 6, f"Expected at least 6 businesses, got {len(biz_list)}"
        print(f"[PASS] GET /api/businesses -> Retrieved {len(biz_list)} businesses.")

        # 1.3 GET /api/businesses/{id} (Existing business)
        res = await client.get(f"/api/businesses/{created_biz_id}")
        assert res.status_code == 200, f"GET /api/businesses/{created_biz_id} failed: {res.text}"
        assert res.json()["id"] == created_biz_id
        print(f"[PASS] GET /api/businesses/{created_biz_id} -> Found business.")

        # 1.4 GET /api/businesses/{id} (404 Not Found)
        res = await client.get("/api/businesses/non-existent-biz-id-12345")
        assert res.status_code == 404, f"Expected 404, got {res.status_code}"
        print("[PASS] GET /api/businesses/non-existent-id -> Correctly returned 404 Not Found.")

        # -------------------------------------------------------------
        # 2. Manager Endpoints
        # -------------------------------------------------------------
        print("\n--- 2. Testing Manager Endpoints ---")
        # 2.1 GET /api/managers (List managers)
        res = await client.get("/api/managers/")
        assert res.status_code == 200, f"GET /api/managers failed: {res.text}"
        mgr_list = res.json()
        assert len(mgr_list) == 18, f"Expected 18 managers, got {len(mgr_list)}"
        print(f"[PASS] GET /api/managers -> Retrieved {len(mgr_list)} managers.")

        # 2.2 GET /api/managers with limit
        res = await client.get("/api/managers/?limit=5")
        assert res.status_code == 200, f"GET /api/managers/?limit=5 failed: {res.text}"
        assert len(res.json()) == 5
        print("[PASS] GET /api/managers/?limit=5 -> Correctly respected limit=5.")

        # 2.3 GET /api/managers/{id} (Sarah Khan)
        res = await client.get("/api/managers/mgr-sarah-khan")
        assert res.status_code == 200, f"GET /api/managers/mgr-sarah-khan failed: {res.text}"
        sarah = res.json()
        assert sarah["name"] == "Sarah Khan"
        assert sarah["salary_expectation"] == 1800.0
        print(f"[PASS] GET /api/managers/mgr-sarah-khan -> Retrieved {sarah['name']} (${sarah['salary_expectation']}/mo).")

        # 2.4 GET /api/managers/{id} (404 Not Found)
        res = await client.get("/api/managers/non-existent-mgr-id-99999")
        assert res.status_code == 404, f"Expected 404, got {res.status_code}"
        print("[PASS] GET /api/managers/non-existent-id -> Correctly returned 404 Not Found.")

        # -------------------------------------------------------------
        # 3. Matching Endpoints
        # -------------------------------------------------------------
        print("\n--- 3. Testing Matching Endpoints ---")
        # 3.1 POST /api/matches/calculate with business_id (FashionCart)
        res = await client.post("/api/matches/calculate", json={"business_id": "biz-fashioncart"})
        assert res.status_code == 200, f"POST /api/matches/calculate failed: {res.text}"
        match_resp = res.json()
        assert match_resp["business_id"] == "biz-fashioncart"
        assert match_resp["total_evaluated"] == 18
        matches = match_resp["matches"]
        assert len(matches) > 0

        top_match = matches[0]
        assert top_match["manager"]["name"] == "Sarah Khan"
        assert 90.0 <= top_match["overall_score"] <= 93.0
        
        # Verify complete 6 factor sub-scores are present
        fs = top_match["factor_scores"]
        for factor_key in ["industry_fit", "skills_fit", "experience_fit", "leadership_fit", "stage_fit", "salary_fit"]:
            assert factor_key in fs, f"Missing factor score: {factor_key}"
            assert 0.0 <= fs[factor_key] <= 100.0
        print(f"[PASS] POST /api/matches/calculate (business_id) -> Top match: {top_match['manager']['name']} ({top_match['overall_score']}%) with all 6 factor scores.")

        # 3.2 POST /api/matches/calculate with inline business_data
        inline_payload = {
            "business_data": {
                "name": "QuickBites Delivery",
                "industry": "Logistics",
                "stage": "Seed",
                "employee_count": 8,
                "salary_budget": 2200.0,
                "required_skills": ["Fleet Dispatch", "Route Optimization", "Supply Chain Optimization"],
                "goals": "Scale local food delivery fleet.",
                "challenges": "Dispatch delays and unoptimized routes."
            }
        }
        res = await client.post("/api/matches/calculate", json=inline_payload)
        assert res.status_code == 200, f"POST /api/matches/calculate (inline) failed: {res.text}"
        inline_match_resp = res.json()
        assert inline_match_resp["total_evaluated"] == 18
        assert len(inline_match_resp["matches"]) > 0
        top_inline = inline_match_resp["matches"][0]
        print(f"[PASS] POST /api/matches/calculate (inline business_data) -> Evaluated 18 candidates. Top match: {top_inline['manager']['name']} ({top_inline['overall_score']}%).")

        # 3.3 POST /api/matches/calculate with empty body (400 Bad Request)
        res = await client.post("/api/matches/calculate", json={})
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        print("[PASS] POST /api/matches/calculate (empty payload) -> Correctly returned 400 Bad Request.")

        # 3.4 POST /api/matches/calculate with invalid business_id (404 Not Found)
        res = await client.post("/api/matches/calculate", json={"business_id": "non-existent-biz-id"})
        assert res.status_code == 404, f"Expected 404, got {res.status_code}"
        print("[PASS] POST /api/matches/calculate (invalid business_id) -> Correctly returned 404 Not Found.")

        # 3.5 GET /api/matches/{business_id} (History lookup)
        res = await client.get("/api/matches/biz-fashioncart")
        assert res.status_code == 200, f"GET /api/matches/biz-fashioncart failed: {res.text}"
        history = res.json()
        assert len(history) > 0, "Expected historical match records to be persisted"
        print(f"[PASS] GET /api/matches/biz-fashioncart -> Retrieved {len(history)} persisted historical match records.")

        # -------------------------------------------------------------
        # 4. Prefix Verification (/api/v1/...)
        # -------------------------------------------------------------
        print("\n--- 4. Testing /api/v1/ Prefix Routing ---")
        res = await client.get("/api/v1/businesses/")
        assert res.status_code == 200
        res = await client.get("/api/v1/managers/")
        assert res.status_code == 200
        print("[PASS] Both /api/... and /api/v1/... routes operate smoothly.")

        print("\n=======================================================")
        print("ALL TASK 5 TESTS PASSED SUCCESSFULLY!")
        print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(test_task5_endpoints())
