import os
import sys
import asyncio
from httpx import AsyncClient, ASGITransport
from pydantic import ValidationError

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.schemas.explanation import MatchExplanation, ExplanationCard
from app.services.ai.explainer_graph import (
    explainability_graph,
    run_explainability_pipeline,
    audit_and_format_node,
    EvaluationState,
    _sanitize_responsible_ai,
)


def test_match_explanation_schema():
    """Verify MatchExplanation Pydantic V2 schema validations and constraints."""
    print("\n--- 1. Testing MatchExplanation Pydantic Schema ---")
    
    # Valid model instance
    valid_exp = MatchExplanation(
        strengths=[
            "5 years of specialized operational experience in fashion e-commerce.",
            "Proven track record scaling order fulfillment and reducing dispatch delays."
        ],
        concerns=[
            "Requires initial orientation to company-specific ERP tooling."
        ],
        missing_requirements=[],
        recommendation_verdict="Highly aligned operational leader for growth-stage fulfillment optimization."
    )
    assert len(valid_exp.strengths) == 2
    assert len(valid_exp.concerns) == 1
    assert valid_exp.missing_requirements == []

    # Invalid: fewer than 2 strengths should raise ValidationError
    raised = False
    try:
        MatchExplanation(
            strengths=["Only one strength"],
            concerns=["One concern"],
            recommendation_verdict="Verdict"
        )
    except ValidationError:
        raised = True
    assert raised, "Expected ValidationError for < 2 strengths"

    # Invalid: 0 concerns should raise ValidationError
    raised = False
    try:
        MatchExplanation(
            strengths=["Strength 1", "Strength 2"],
            concerns=[],
            recommendation_verdict="Verdict"
        )
    except ValidationError:
        raised = True
    assert raised, "Expected ValidationError for 0 concerns"

    print("[PASS] MatchExplanation schema validation constraints verified.")


def test_explainer_graph_structure():
    """Verify LangGraph compilation and workflow node registrations."""
    print("\n--- 2. Testing LangGraph Graph Compilation ---")
    assert explainability_graph is not None
    # Graph nodes inspection
    nodes = explainability_graph.nodes
    assert "generate_explanation" in nodes
    assert "audit_and_format" in nodes
    print("[PASS] LangGraph StateGraph compiled with generate_explanation and audit_and_format nodes.")


async def test_sarah_khan_fashioncart_pipeline():
    """Test full explainability pipeline for benchmark candidate Sarah Khan & FashionCart."""
    print("\n--- 3. Testing Pipeline: Sarah Khan & FashionCart ---")
    
    business = {
        "id": "biz-fashioncart",
        "name": "FashionCart",
        "industry": "E-Commerce",
        "stage": "Growth",
        "salary_budget": 2000.0,
        "goals": "Double revenue within 12 months and streamline dispatch operations.",
        "challenges": "Fulfillment process is disorganized and employees lack defined roles.",
        "required_skills": ["Operations Management", "Process Optimization", "Team Management", "Supply Chain"],
        "required_experience": ["E-commerce operations", "Warehouse management"]
    }

    manager = {
        "id": "mgr-sarah-khan",
        "name": "Sarah Khan",
        "role_title": "Operations Lead",
        "experience_years": 5,
        "expected_salary": 1800.0,
        "work_arrangement": "Remote/Hybrid",
        "industries": ["E-Commerce", "Retail"],
        "skills": ["Operations Management", "Supply Chain", "Team Management", "Process Optimization"],
        "previous_roles": ["Head of Operations at Daraz", "Supply Chain Supervisor"],
        "achievements": ["Scaled fulfillment team from 3 to 15", "Reduced order backlog by 40%"],
        "verified_stages": ["Growth", "Early"],
        "verified_track_record": "Led operational turnaround of e-commerce delivery hubs."
    }

    factor_scores = {
        "industry_fit": 100.0,
        "skills_fit": 95.0,
        "experience_fit": 85.0,
        "leadership_fit": 85.0,
        "stage_fit": 90.0,
        "salary_fit": 100.0
    }
    overall_score = 91.4

    result = await run_explainability_pipeline(
        business=business,
        manager=manager,
        factor_scores=factor_scores,
        overall_score=overall_score
    )

    # Output structure validation
    assert isinstance(result, dict)
    assert result["manager_id"] == "mgr-sarah-khan"
    # Strict score isolation: model/pipeline must never alter numerical scores
    assert result["overall_score"] == 91.4
    assert result["factor_scores"] == factor_scores
    
    assert 2 <= len(result["strengths"]) <= 4
    assert 1 <= len(result["concerns"]) <= 3
    assert isinstance(result["missing_requirements"], list)
    assert len(result["verdict"]) > 10

    print(f"Strengths ({len(result['strengths'])}): {result['strengths']}")
    print(f"Concerns ({len(result['concerns'])}): {result['concerns']}")
    print(f"Missing Requirements: {result['missing_requirements']}")
    print(f"Verdict: {result['verdict']}")
    print("[PASS] Full explainability pipeline completed with score isolation and valid decision card structure.")


async def test_salary_budget_tradeoff_framing():
    """Verify that candidates above budget have salary identified as a trade-off, not a dismissal."""
    print("\n--- 4. Testing Salary Budget Trade-Off Framing (Ali Ahmed) ---")
    
    business = {
        "id": "biz-fashioncart",
        "name": "FashionCart",
        "industry": "E-Commerce",
        "stage": "Growth",
        "salary_budget": 2000.0,
        "required_skills": ["Operations Management"]
    }

    manager = {
        "id": "mgr-ali-ahmed",
        "name": "Ali Ahmed",
        "role_title": "VP Operations",
        "experience_years": 12,
        "expected_salary": 2600.0,  # $600 above budget
        "industries": ["Corporate Logistics", "Retail"],
        "skills": ["Operations Management", "Executive Leadership"],
        "achievements": ["Managed $10M logistics budget"],
        "verified_stages": ["Scale", "Enterprise"]
    }

    factor_scores = {
        "industry_fit": 80.0,
        "skills_fit": 85.0,
        "experience_fit": 95.0,
        "leadership_fit": 95.0,
        "stage_fit": 50.0,
        "salary_fit": 30.0
    }
    overall_score = 72.4

    result = await run_explainability_pipeline(
        business=business,
        manager=manager,
        factor_scores=factor_scores,
        overall_score=overall_score
    )

    concerns_text = " ".join(result["concerns"]).lower()
    verdict_text = result["verdict"].lower()
    
    # Must mention compensation / salary / budget trade-off
    has_budget_mention = any(term in concerns_text or term in verdict_text for term in ["salary", "budget", "compensation", "2,600", "2600"])
    assert has_budget_mention, "Pipeline failed to identify above-budget salary as a trade-off"
    print(f"Concerns noted: {result['concerns']}")
    print("[PASS] Above-budget salary properly highlighted as a trade-off.")


async def test_zero_hallucination_and_fairness_audit():
    """Verify that audit node intercepts ungrounded claims and filters demographic attributes."""
    print("\n--- 5. Testing Zero-Hallucination and Responsible AI Audit Node ---")
    
    business = {
        "id": "biz-test",
        "name": "TestBiz",
        "required_skills": ["Quantum Computing", "Operations Management"]
    }

    manager = {
        "id": "mgr-001",
        "name": "John Doe",
        "skills": ["Operations Management", "Supply Chain"],
        "previous_roles": ["Operations Coordinator"],
        "achievements": ["Optimized dispatch workflow"],
        "verified_stages": ["Growth"]
    }

    # Raw explanation with hallucinated skill and protected class reference
    raw_exp = MatchExplanation(
        strengths=[
            "As a 28-year-old male candidate, he has proven mastery in Quantum Computing algorithms.",
            "Demonstrated guaranteed success in optimizing warehouse processes."
        ],
        concerns=[
            "Requires time to adapt to corporate processes."
        ],
        missing_requirements=[],
        recommendation_verdict="Candidate will guarantee 100% success for TestBiz."
    )

    state: EvaluationState = {
        "business_profile": business,
        "manager_profile": manager,
        "factor_scores": {"skills_fit": 75.0},
        "overall_score": 75.0,
        "raw_explanation": raw_exp,
        "final_explanation": None
    }

    audited = await audit_and_format_node(state)
    final_output = audited["final_explanation"]
    
    strengths_text = " ".join(final_output["strengths"])
    verdict_text = final_output["verdict"]

    # Responsible AI checks: Age and gender words should be sanitized
    assert "28-year-old" not in strengths_text
    assert "he has" not in strengths_text
    assert "guaranteed" not in strengths_text.lower()
    assert "guarantee" not in verdict_text.lower()

    # Zero-hallucination check: Quantum Computing is not in manager profile,
    # so it must be flagged or transferred to missing_requirements
    quantum_flagged = any("Quantum Computing" in m for m in final_output["missing_requirements"]) or \
                      any("not verified" in s.lower() for s in final_output["strengths"] if "quantum" in s.lower())
    assert quantum_flagged, "Audit node failed to detect ungrounded skill (Quantum Computing)"

    print(f"Audited Strengths: {final_output['strengths']}")
    print(f"Audited Missing: {final_output['missing_requirements']}")
    print(f"Audited Verdict: {final_output['verdict']}")
    print("[PASS] Responsible AI and Zero-Hallucination audits successfully sanitized and flagged output.")


async def test_explain_endpoint_http():
    """Test HTTP POST /api/matches/explain and POST /api/v1/matches/explain."""
    print("\n--- 6. Testing HTTP POST /api/matches/explain Endpoint ---")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Obtain auth token
        login_res = await client.post("/api/auth/login", json={"email": "founder@bizmatch.ai", "password": "password123"})
        headers = {}
        if login_res.status_code == 200:
            token = login_res.json().get("access_token")
            if token:
                headers = {"Authorization": f"Bearer {token}"}

        # Request explanation for Sarah Khan and FashionCart
        res = await client.post("/api/matches/explain", json={
            "business_id": "biz-fashioncart",
            "manager_id": "mgr-sarah-khan"
        }, headers=headers)
        assert res.status_code == 200, f"Endpoint failed: {res.text}"
        body = res.json()
        assert body["success"] is True
        card = body["data"]
        assert "strengths" in card
        assert "concerns" in card
        assert "missing_requirements" in card
        assert "verdict" in card
        assert "manager_id" in card or card.get("manager_id") == "mgr-sarah-khan"
        assert len(card["strengths"]) >= 2
        assert len(card["concerns"]) >= 1
        print(f"[PASS] POST /api/matches/explain returned 200 OK with valid decision card.")

        # Test with /v1 prefix
        res_v1 = await client.post("/api/v1/matches/explain", json={
            "business_id": "biz-fashioncart",
            "manager_id": "mgr-sarah-khan"
        }, headers=headers)
        assert res_v1.status_code == 200
        print(f"[PASS] POST /api/v1/matches/explain returned 200 OK.")


if __name__ == "__main__":
    test_match_explanation_schema()
    test_explainer_graph_structure()
    asyncio.run(test_sarah_khan_fashioncart_pipeline())
    asyncio.run(test_salary_budget_tradeoff_framing())
    asyncio.run(test_zero_hallucination_and_fairness_audit())
    asyncio.run(test_explain_endpoint_http())
    print("\n=======================================================")
    print("ALL TASK 7 EXPLAINER TESTS PASSED SUCCESSFULLY!")
    print("=======================================================\n")
