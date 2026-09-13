import os
import sys
import asyncio

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from httpx import AsyncClient, ASGITransport
from main import app

async def test_all_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        print("\n=== TESTING ALL ENDPOINTS ===")
        
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        assert data["status"] == "healthy"
        print(f"[PASS] GET /health -> {data}")
        
        # 2. GET /api/businesses/
        res = await client.get("/api/businesses/")
        assert res.status_code == 200, f"GET businesses failed: {res.text}"
        bizs = res.json()
        assert len(bizs) >= 5, f"Expected at least 5 businesses, got {len(bizs)}"
        print(f"[PASS] GET /api/businesses/ -> {len(bizs)} businesses retrieved.")
        
        # 3. POST /api/businesses/analyze-requirements
        res = await client.post("/api/businesses/analyze-requirements", json={
            "goals": "Double revenue and expand e-commerce operations in 12 months.",
            "challenges": "Disorganized order fulfillment and unclear employee roles.",
            "raw_preferences": "Need operations leader with e-commerce experience under $2000/mo."
        })
        assert res.status_code == 200, f"Analyze requirements failed: {res.text}"
        assert res.json()["success"] is True
        print(f"[PASS] POST /api/businesses/analyze-requirements -> success=True")
        
        # 4. GET /api/managers/
        res = await client.get("/api/managers/")
        assert res.status_code == 200, f"GET managers failed: {res.text}"
        mgrs = res.json()
        assert len(mgrs) == 18, f"Expected 18 managers, got {len(mgrs)}"
        print(f"[PASS] GET /api/managers/ -> {len(mgrs)} managers retrieved.")
        
        # 5. POST /api/matches/calculate
        res = await client.post("/api/matches/calculate", json={"business_id": "biz-fashioncart"})
        assert res.status_code == 200, f"Matches calculate failed: {res.text}"
        match_data = res.json()
        matches = match_data.get("matches") or match_data.get("data", [])
        assert len(matches) > 0, "No matches calculated"
        top_match = matches[0]
        top_mgr_id = top_match.get("manager_id") or top_match["manager"]["id"]
        print(f"[PASS] POST /api/matches/calculate -> {len(matches)} matches returned. Top match: {top_mgr_id} with score {top_match['overall_score']}")
        
        # 6. POST /api/matches/explain
        res = await client.post("/api/matches/explain", json={
            "business_id": "biz-fashioncart",
            "manager_id": top_mgr_id
        })
        assert res.status_code == 200, f"Matches explain failed: {res.text}"
        explanation = res.json()["data"]
        assert "verdict" in explanation
        assert len(explanation["strengths"]) > 0
        print(f"[PASS] POST /api/matches/explain -> Verdict: {explanation['verdict']}")
        
        print("=== ALL ENDPOINTS VERIFIED AND PASSING SUCCESSFULLY! ===\n")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
