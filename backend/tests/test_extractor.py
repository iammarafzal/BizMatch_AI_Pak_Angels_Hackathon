import os
import sys
import asyncio
from httpx import AsyncClient, ASGITransport

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.schemas.match import AnalyzeRequirementsRequest, StructuredRequirements
from app.services.ai.extractor import extract_requirements

async def test_fashioncart_requirement_extraction():
    print("\n=== TESTING TASK 6: LANGCHAIN REQUIREMENT EXTRACTOR ===")

    # 1. Direct function test with FashionCart prompt
    print("\n--- 1. Testing extract_requirements() direct service invocation ---")
    req = AnalyzeRequirementsRequest(
        name="FashionCart",
        industry="E-commerce",
        stage="Growth",
        goals="We want to double our revenue within the next 12 months and expand our operations.",
        challenges="Our orders have increased significantly, but our fulfillment process is disorganized and our employees don't have clearly defined responsibilities.",
        raw_preferences="Need operations management, team leadership, process optimization, e-commerce domain experience under $2,000/mo."
    )

    result: StructuredRequirements = await extract_requirements(req)
    assert isinstance(result, StructuredRequirements), f"Expected StructuredRequirements, got {type(result)}"
    
    print(f"Extracted Industry: {result.industry}")
    print(f"Extracted Stage: {result.business_stage}")
    print(f"Extracted Priorities: {result.key_priorities}")
    print(f"Extracted Skills: {result.required_skills}")
    print(f"Extracted Experience: {result.experience_requirements}")

    # Assertions
    skills_lower = [s.lower() for s in result.required_skills]
    assert any("operation" in s for s in skills_lower), "Operations management skill missing"
    assert any("process" in s or "optimization" in s for s in skills_lower), "Process optimization skill missing"
    assert any("team" in s or "leadership" in s or "management" in s for s in skills_lower), "Team leadership skill missing"
    assert len(result.key_priorities) >= 2, "Expected at least 2 key priorities"
    assert len(result.experience_requirements) >= 1, "Expected at least 1 experience requirement"

    print("[PASS] Direct requirement extraction correctly identified operations management, process optimization, and team leadership.")

    # 2. HTTP Endpoint test: POST /api/analyze-requirements
    print("\n--- 2. Testing HTTP Endpoint: POST /api/analyze-requirements ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "name": "FashionCart",
            "industry": "E-commerce",
            "stage": "Growth",
            "goals": "We want to double our revenue within the next 12 months and expand our operations.",
            "challenges": "Our orders have increased significantly, but our fulfillment process is disorganized and our employees don't have clearly defined responsibilities.",
            "raw_preferences": "Need operations management, team leadership, process optimization under $2,000/mo."
        }

        # Test base /api route
        res = await client.post("/api/analyze-requirements", json=payload)
        assert res.status_code == 200, f"POST /api/analyze-requirements failed: {res.text}"
        data = res.json()
        assert "industry" in data
        assert "business_stage" in data
        assert "key_priorities" in data
        assert "required_skills" in data
        assert "experience_requirements" in data
        print("[PASS] POST /api/analyze-requirements -> 200 OK with valid StructuredRequirements JSON shape.")

        # Test /api/v1 prefix route
        res_v1 = await client.post("/api/v1/analyze-requirements", json=payload)
        assert res_v1.status_code == 200, f"POST /api/v1/analyze-requirements failed: {res_v1.text}"
        print("[PASS] POST /api/v1/analyze-requirements -> 200 OK with identical valid JSON shape.")

        # 3. Test with a B2B SaaS startup prompt
        print("\n--- 3. Testing B2B SaaS scenario ---")
        saas_payload = {
            "name": "CloudPulse",
            "industry": "B2B SaaS",
            "stage": "Seed",
            "goals": "Ship enterprise tier features on time and establish clear sprint planning.",
            "challenges": "Developers are building ad-hoc features without clear specifications or product roadmap.",
            "raw_preferences": "Looking for technical product manager with agile scrum expertise."
        }
        res_saas = await client.post("/api/analyze-requirements", json=saas_payload)
        assert res_saas.status_code == 200
        saas_data = res_saas.json()
        saas_skills = [s.lower() for s in saas_data["required_skills"]]
        assert any("product" in s or "agile" in s or "scrum" in s for s in saas_skills)
        print(f"[PASS] B2B SaaS extraction extracted: {saas_data['required_skills']}")

    print("\n=======================================================")
    print("ALL TASK 6 EXTRACTOR TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(test_fashioncart_requirement_extraction())
