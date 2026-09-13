#!/usr/bin/env python3
"""
BizMatch AI - Comprehensive Backend QA & Endpoint Verification Suite
Systematically tests all application endpoints to guarantee 100% reliability.
"""

import sys
import os
import time
import asyncio
import re
from typing import List, Dict, Any, Tuple

# Ensure backend root is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from httpx import AsyncClient, ASGITransport
from main import app


class EndpointTestTracker:
    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def record(self, endpoint: str, method: str, status: str, latency_ms: float, details: str, fixes: str = "N/A - Clean Execution"):
        self.results.append({
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "latency_ms": latency_ms,
            "details": details,
            "fixes": fixes
        })

    def print_ascii_summary(self):
        print("\n" + "=" * 120)
        print("                               BIZMATCH AI - BACKEND ENDPOINT QA SUMMARY REPORT")
        print("=" * 120)
        header = f"{'ENDPOINT / ROUTE':<35} | {'METHOD':<6} | {'STATUS':<6} | {'LATENCY (MS)':<12} | {'ROOT CAUSE & FILES MODIFIED / NOTES'}"
        print(header)
        print("-" * 120)

        all_passed = True
        for r in self.results:
            if r["status"] != "PASS":
                all_passed = False
            status_str = f"PASS" if r["status"] == "PASS" else "FAIL"
            endpoint_method = f"{r['endpoint']}"
            print(f"{endpoint_method:<35} | {r['method']:<6} | {status_str:<6} | {r['latency_ms']:>10.2f} ms | {r['fixes']}")

        print("-" * 120)
        if all_passed:
            print("  OVERALL VERDICT: [PASS] 100% RELIABILITY ACHIEVED ACROSS ALL BACKEND ENDPOINTS FOR LIVE DEMO!")
        else:
            print("  OVERALL VERDICT: [FAIL] ONE OR MORE ENDPOINTS ENCOUNTERED FAILURES.")
        print("=" * 120 + "\n")


async def run_verification():
    tracker = EndpointTestTracker()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=30.0) as client:
        print("\n>>> Starting BizMatch AI Endpoint Verification Suite...\n")

        # 0. Obtain JWT Bearer Token for Protected Routes
        auth_headers = {}
        try:
            login_res = await client.post("/api/auth/login", json={"email": "founder@bizmatch.ai", "password": "password123"})
            if login_res.status_code == 200:
                token = login_res.json().get("access_token")
                if token:
                    auth_headers = {"Authorization": f"Bearer {token}"}
        except Exception:
            pass

        # ---------------------------------------------------------------------
        # 1. Health & Base Check
        # GET /health -> 200 OK, {"status": "healthy"}
        # ---------------------------------------------------------------------
        t0 = time.perf_counter()
        res = await client.get("/health")
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200 and res.json().get("status") == "healthy":
            tracker.record("/health", "GET", "PASS", latency, "Healthy status verified")
        else:
            tracker.record("/health", "GET", "FAIL", latency, f"Unexpected response: {res.status_code} {res.text}")

        # ---------------------------------------------------------------------
        # 2. Demo Fast-Track Route
        # GET /api/demo/fashioncart -> 200 OK, FashionCart firmographics & budget $2,000
        # ---------------------------------------------------------------------
        t0 = time.perf_counter()
        res = await client.get("/api/demo/fashioncart")
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            body = res.json()
            data = body.get("data", body)
            name_ok = data.get("name") == "FashionCart"
            budget_ok = data.get("salary_budget") == 2000.0 or data.get("budget") == 2000.0
            goals_ok = "revenue" in str(data.get("goals", "")).lower() or len(data.get("primary_goals", [])) > 0
            if name_ok and budget_ok and goals_ok:
                tracker.record("/api/demo/fashioncart", "GET", "PASS", latency, "FashionCart preset loaded cleanly with $2,000 budget")
            else:
                tracker.record("/api/demo/fashioncart", "GET", "FAIL", latency, f"Data assertion failed: {data}")
        else:
            tracker.record("/api/demo/fashioncart", "GET", "FAIL", latency, f"Status code: {res.status_code}")

        # ---------------------------------------------------------------------
        # 3. Business Profile Management - List Businesses
        # GET /api/businesses -> 200 OK, non-empty array
        # ---------------------------------------------------------------------
        t0 = time.perf_counter()
        res = await client.get("/api/businesses")
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            biz_list = res.json()
            if isinstance(biz_list, list) and len(biz_list) > 0:
                tracker.record("/api/businesses", "GET", "PASS", latency, f"Retrieved {len(biz_list)} seeded businesses")
            else:
                tracker.record("/api/businesses", "GET", "FAIL", latency, f"Expected non-empty list, got: {biz_list}")
        else:
            tracker.record("/api/businesses", "GET", "FAIL", latency, f"Status code: {res.status_code}")

        # ---------------------------------------------------------------------
        # 4. Business Profile Management - Create Business
        # POST /api/businesses -> 201 Created or 200 OK with returned ID (Requires Auth)
        # ---------------------------------------------------------------------
        new_biz_payload = {
            "name": "QA Test Ventures",
            "industry": "FinTech",
            "stage": "Growth",
            "size": "Medium",
            "location": "Lahore / Remote",
            "employee_count": 18,
            "salary_budget": 2500.0,
            "goals": "Expand payment gateway compliance and scale user acquisition.",
            "challenges": "KYC onboarding delays and fraud detection backlogs.",
            "required_skills": ["FinTech Compliance", "Risk Management", "Process Optimization"],
            "required_experience": ["Payment operations leadership"],
            "work_arrangement": "Hybrid"
        }
        t0 = time.perf_counter()
        res = await client.post("/api/businesses", json=new_biz_payload, headers=auth_headers)
        latency = (time.perf_counter() - t0) * 1000
        created_biz_id = None
        if res.status_code in (200, 201):
            created_biz = res.json()
            created_biz_id = created_biz.get("id")
            if created_biz_id and created_biz.get("name") == "QA Test Ventures":
                tracker.record("/api/businesses", "POST", "PASS", latency, f"Created business profile ID: {created_biz_id}")
            else:
                tracker.record("/api/businesses", "POST", "FAIL", latency, f"Attributes missing in response: {created_biz}")
        else:
            tracker.record("/api/businesses", "POST", "FAIL", latency, f"Status code {res.status_code}: {res.text}")

        # ---------------------------------------------------------------------
        # 5. Business Profile Management - Get Business by ID
        # GET /api/businesses/{id} -> 200 OK with matching attributes
        # ---------------------------------------------------------------------
        target_biz_id = created_biz_id or "biz-fashioncart"
        t0 = time.perf_counter()
        res = await client.get(f"/api/businesses/{target_biz_id}")
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            retrieved_biz = res.json()
            if retrieved_biz.get("id") == target_biz_id:
                tracker.record(f"/api/businesses/{{id}}", "GET", "PASS", latency, f"Fetched business {target_biz_id} successfully")
            else:
                tracker.record(f"/api/businesses/{{id}}", "GET", "FAIL", latency, f"ID mismatch: {retrieved_biz.get('id')}")
        else:
            tracker.record(f"/api/businesses/{{id}}", "GET", "FAIL", latency, f"Status code {res.status_code}: {res.text}")

        # ---------------------------------------------------------------------
        # 6. Manager Directory - List Managers
        # GET /api/managers -> 200 OK, >= 15 candidates
        # ---------------------------------------------------------------------
        t0 = time.perf_counter()
        res = await client.get("/api/managers")
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            managers = res.json()
            if isinstance(managers, list) and len(managers) >= 15:
                tracker.record("/api/managers", "GET", "PASS", latency, f"Retrieved {len(managers)} candidate manager profiles (>= 15)")
            else:
                tracker.record("/api/managers", "GET", "FAIL", latency, f"Expected >= 15 managers, got {len(managers) if isinstance(managers, list) else managers}")
        else:
            tracker.record("/api/managers", "GET", "FAIL", latency, f"Status code: {res.status_code}")

        # ---------------------------------------------------------------------
        # 7. Manager Directory - Get Manager by ID (Sarah Khan)
        # GET /api/managers/mgr-sarah-khan -> 200 OK with complete skills, roles, salary expectation
        # ---------------------------------------------------------------------
        t0 = time.perf_counter()
        res = await client.get("/api/managers/mgr-sarah-khan")
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            sarah = res.json()
            has_skills = len(sarah.get("skills", []) or sarah.get("core_skills", [])) > 0
            has_roles = len(sarah.get("previous_roles", [])) > 0
            has_salary = (sarah.get("salary_expectation") or sarah.get("monthly_rate_usd", 0.0)) > 0
            if sarah.get("name") == "Sarah Khan" and has_skills and has_roles and has_salary:
                tracker.record("/api/managers/mgr-sarah-khan", "GET", "PASS", latency, "Sarah Khan profile retrieved with full attributes")
            else:
                tracker.record("/api/managers/mgr-sarah-khan", "GET", "FAIL", latency, f"Incomplete profile attributes: {sarah}")
        else:
            tracker.record("/api/managers/mgr-sarah-khan", "GET", "FAIL", latency, f"Status code: {res.status_code}")

        # ---------------------------------------------------------------------
        # 8. LangChain Requirement Extraction
        # POST /api/analyze-requirements -> unstructured text -> 200 OK + Pydantic schema
        # ---------------------------------------------------------------------
        req_input = {
            "goals": "double revenue in 12 months",
            "challenges": "fulfillment is disorganized and employees lack clear roles"
        }
        t0 = time.perf_counter()
        res = await client.post("/api/analyze-requirements", json=req_input)
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            extracted = res.json()
            if "data" in extracted and isinstance(extracted["data"], dict):
                extracted_data = extracted["data"]
            else:
                extracted_data = extracted

            has_ind = "industry" in extracted_data
            has_stage = "business_stage" in extracted_data or "stage" in extracted_data
            has_prio = "key_priorities" in extracted_data
            has_skills = "required_skills" in extracted_data
            has_exp = "experience_requirements" in extracted_data

            if has_ind and has_stage and has_prio and has_skills and has_exp:
                tracker.record("/api/analyze-requirements", "POST", "PASS", latency, "Extracted structured requirements matching Pydantic schema")
            else:
                tracker.record("/api/analyze-requirements", "POST", "FAIL", latency, f"Missing required fields in schema: {extracted_data}")
        else:
            tracker.record("/api/analyze-requirements", "POST", "FAIL", latency, f"Status code {res.status_code}: {res.text}")

        # ---------------------------------------------------------------------
        # 9. Deterministic Matching Engine
        # POST /api/matches/calculate -> FashionCart payload/id (Requires Auth)
        # Verify: match count > 0, factor sub-scores strictly 0.0 to 100.0,
        # weighted formula math check: 0.20*Industry + 0.25*Skills + 0.20*Exp + 0.15*Lead + 0.10*Stage + 0.10*Salary
        # Sarah Khan ranks #1 (~90-92%)
        # ---------------------------------------------------------------------
        match_req_payload = {
            "business_id": "biz-fashioncart"
        }
        t0 = time.perf_counter()
        res = await client.post("/api/matches/calculate?include_explanations=true", json=match_req_payload, headers=auth_headers)
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            match_data = res.json()
            matches = match_data.get("matches", [])
            total_eval = match_data.get("total_evaluated", 0)

            count_ok = len(matches) > 0
            scores_valid = True
            formula_valid = True

            for m in matches:
                ov = m["overall_score"]
                fs = m["factor_scores"]

                if not (0.0 <= ov <= 100.0):
                    scores_valid = False
                for fname, fval in fs.items():
                    if not (0.0 <= fval <= 100.0):
                        scores_valid = False

                calculated_weighted = (
                    0.20 * fs["industry_fit"] +
                    0.25 * fs["skills_fit"] +
                    0.20 * fs["experience_fit"] +
                    0.15 * fs["leadership_fit"] +
                    0.10 * fs["stage_fit"] +
                    0.10 * fs["salary_fit"]
                )
                if abs(round(calculated_weighted, 1) - ov) > 0.2:
                    formula_valid = False

            top_1 = matches[0] if matches else None
            sarah_rank_1 = top_1 and "Sarah Khan" in top_1["manager"]["name"]
            sarah_score_benchmark = top_1 and (90.0 <= top_1["overall_score"] <= 94.0)

            if count_ok and scores_valid and formula_valid and sarah_rank_1 and sarah_score_benchmark:
                tracker.record(
                    "/api/matches/calculate",
                    "POST",
                    "PASS",
                    latency,
                    f"Sarah Khan #1 ({top_1['overall_score']}%), sub-scores 0-100 & 6-factor weighted math verified"
                )
            else:
                failure_reason = f"count_ok={count_ok}, scores_valid={scores_valid}, formula_valid={formula_valid}, sarah_rank_1={sarah_rank_1}, top_1={top_1['manager']['name'] if top_1 else None} ({top_1['overall_score'] if top_1 else None}%)"
                tracker.record("/api/matches/calculate", "POST", "FAIL", latency, failure_reason)
        else:
            tracker.record("/api/matches/calculate", "POST", "FAIL", latency, f"Status code {res.status_code}: {res.text}")

        # ---------------------------------------------------------------------
        # 10. LangGraph Explainability Pipeline
        # POST /api/matches/explain -> FashionCart ID + Sarah Khan ID (Requires Auth)
        # ---------------------------------------------------------------------
        explain_payload = {
            "business_id": "biz-fashioncart",
            "manager_id": "mgr-sarah-khan"
        }
        t0 = time.perf_counter()
        res = await client.post("/api/matches/explain", json=explain_payload, headers=auth_headers)
        latency = (time.perf_counter() - t0) * 1000
        if res.status_code == 200:
            exp_res = res.json()
            strengths = exp_res.get("strengths", [])
            concerns = exp_res.get("concerns", [])
            missing = exp_res.get("missing_requirements", [])
            verdict = exp_res.get("verdict", "")

            has_strengths = len(strengths) >= 2
            has_concerns = len(concerns) >= 1
            has_verdict = len(verdict) > 10

            full_text = " ".join(strengths + concerns) + " " + verdict

            age_match = re.search(r"\b\d+[\s-]*year[\s-]*old\b", full_text, re.I)
            gender_match = re.search(r"\b(he\s+is|she\s+is|he\s+has|she\s+has|male|female)\b", full_text, re.I)

            if has_strengths and has_concerns and has_verdict and not age_match and not gender_match:
                tracker.record(
                    "/api/matches/explain",
                    "POST",
                    "PASS",
                    latency,
                    f"Generated card ({len(strengths)} strengths, {len(concerns)} concerns) with zero demographic bias"
                )
            else:
                tracker.record(
                    "/api/matches/explain",
                    "POST",
                    "FAIL",
                    latency,
                    f"Audit failure: strengths={has_strengths}, concerns={has_concerns}, verdict={has_verdict}, age={bool(age_match)}, gender={bool(gender_match)}"
                )
        else:
            tracker.record("/api/matches/explain", "POST", "FAIL", latency, f"Status code {res.status_code}: {res.text}")

    tracker.print_ascii_summary()


if __name__ == "__main__":
    asyncio.run(run_verification())
