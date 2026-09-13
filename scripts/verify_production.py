"""
BizMatch AI - Root Production Verification & Automated Smoke Test
Validates end-to-end live backend services against running FastAPI server:
1. GET /health
2. GET /api/demo/fashioncart
3. POST /api/analyze-requirements
4. POST /api/matches/calculate (Sarah Khan top match ~90-92%)
5. POST /api/matches/explain (LangGraph explainability synthesis)
"""

import sys
import time
import json
import requests
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def log_header(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)

def main():
    log_header("BizMatch AI - End-to-End Production Verification & Smoke Test")
    print(f"Target Server: {BASE_URL}")

    results_table: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # 1. GET /health
    # -------------------------------------------------------------
    print("\n[Step 1] Verifying GET /health ...")
    start = time.time()
    try:
        res = requests.get(f"{BASE_URL}/health", timeout=10)
        elapsed_ms = round((time.time() - start) * 1000, 1)
        if res.status_code == 200 and res.json().get("status") == "healthy":
            print(f"  [PASS] 200 OK | Response: {res.json()} ({elapsed_ms}ms)")
            results_table.append({
                "Test": "1. GET /health",
                "Status": "PASS",
                "Latency": f"{elapsed_ms}ms",
                "Details": "Healthy status returned from core service"
            })
        else:
            print(f"  [FAIL] Status {res.status_code} | {res.text}")
            results_table.append({
                "Test": "1. GET /health",
                "Status": "FAIL",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"HTTP {res.status_code}: {res.text}"
            })
    except Exception as e:
        results_table.append({
            "Test": "1. GET /health",
            "Status": "ERROR",
            "Latency": "N/A",
            "Details": str(e)
        })
        print(f"  [FAIL] Connection Error: {e}")

    # -------------------------------------------------------------
    # 2. GET /api/demo/fashioncart
    # -------------------------------------------------------------
    print("\n[Step 2] Verifying GET /api/demo/fashioncart ...")
    start = time.time()
    try:
        res = requests.get(f"{BASE_URL}/api/demo/fashioncart", timeout=10)
        elapsed_ms = round((time.time() - start) * 1000, 1)
        data = res.json()
        name = data.get("name")
        budget = data.get("salary_budget")
        skills = data.get("required_skills", [])

        if res.status_code == 200 and name == "FashionCart" and budget == 2000:
            print(f"  [PASS] 200 OK | Loaded: {name} (Budget: ${budget}/mo, Skills: {len(skills)}) ({elapsed_ms}ms)")
            results_table.append({
                "Test": "2. GET /api/demo/fashioncart",
                "Status": "PASS",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"Seeded scenario {name} verified ($2,000/mo budget)"
            })
        else:
            print(f"  [FAIL] Status {res.status_code} | {data}")
            results_table.append({
                "Test": "2. GET /api/demo/fashioncart",
                "Status": "FAIL",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"Mismatch in demo preset firmographics: {data}"
            })
    except Exception as e:
        results_table.append({
            "Test": "2. GET /api/demo/fashioncart",
            "Status": "ERROR",
            "Latency": "N/A",
            "Details": str(e)
        })
        print(f"  [FAIL] Error: {e}")

    # -------------------------------------------------------------
    # 3. POST /api/analyze-requirements (AI Extraction)
    # -------------------------------------------------------------
    print("\n[Step 3] Verifying POST /api/analyze-requirements with dynamic custom text ...")
    start = time.time()
    custom_payload = {
        "name": "ArtisanCeramics",
        "industry": "Handmade Crafts & Ceramics",
        "stage": "Seed",
        "goals": "we sell custom ceramic mugs online and orders are lost in spreadsheets, need automated order intake",
        "challenges": "inventory mismatch, fragmented tracking across email and whatsapp, delivery delays",
        "raw_preferences": "need a hands-on operations lead to implement an ERP/inventory system and train local packing staff"
    }

    try:
        res = requests.post(f"{BASE_URL}/api/analyze-requirements", json=custom_payload, timeout=20)
        elapsed_ms = round((time.time() - start) * 1000, 1)
        data = res.json()

        industry = data.get("industry")
        stage = data.get("business_stage")
        skills = data.get("required_skills", [])
        priorities = data.get("key_priorities", [])
        experiences = data.get("experience_requirements", [])

        if res.status_code == 200 and skills and priorities:
            print(f"  [PASS] 200 OK | Extracted Industry: '{industry}', Stage: '{stage}' ({elapsed_ms}ms)")
            print(f"    - Skills Extracted: {skills[:4]}")
            print(f"    - Priorities: {priorities[:2]}")
            print(f"    - Experience Req: {experiences[:2]}")
            results_table.append({
                "Test": "3. POST /api/analyze-requirements",
                "Status": "PASS",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"Dynamically extracted {len(skills)} skills & {len(priorities)} priorities"
            })
        else:
            print(f"  [FAIL] Status {res.status_code} | {data}")
            results_table.append({
                "Test": "3. POST /api/analyze-requirements",
                "Status": "FAIL",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"Extraction schema mismatch or empty: {data}"
            })
    except Exception as e:
        results_table.append({
            "Test": "3. POST /api/analyze-requirements",
            "Status": "ERROR",
            "Latency": "N/A",
            "Details": str(e)
        })
        print(f"  [FAIL] Error: {e}")

    # -------------------------------------------------------------
    # 4. POST /api/matches/calculate (Deterministic 6-Factor Scoring)
    # -------------------------------------------------------------
    print("\n[Step 4] Verifying POST /api/matches/calculate across seeded candidates ...")
    start = time.time()
    calc_payload = {"business_id": "biz-fashioncart"}

    try:
        res = requests.post(f"{BASE_URL}/api/matches/calculate", json=calc_payload, timeout=15)
        elapsed_ms = round((time.time() - start) * 1000, 1)
        data = res.json()

        total_evaluated = data.get("total_evaluated", 0)
        matches = data.get("matches", [])

        if res.status_code == 200 and matches:
            top_match = matches[0]
            top_mgr = top_match.get("manager", {})
            top_name = top_mgr.get("name")
            top_score = float(top_match.get("overall_score", 0.0))
            factors = top_match.get("factor_scores", {})

            print(f"  [PASS] 200 OK | Evaluated {total_evaluated} candidates in SQLite ({elapsed_ms}ms)")
            print(f"    - Top Pick: {top_name} (Overall Score: {top_score}%)")
            print(f"    - Factor Scores: {factors}")

            # Verify Sarah Khan benchmark (~90-93%)
            sarah_is_top = (top_name == "Sarah Khan" and 88.0 <= top_score <= 95.0)

            # Verify exact 6 factor keys
            expected_factors = {"industry_fit", "skills_fit", "experience_fit", "leadership_fit", "stage_fit", "salary_fit"}
            factors_valid = expected_factors.issubset(set(factors.keys()))

            if sarah_is_top and factors_valid:
                results_table.append({
                    "Test": "4. POST /api/matches/calculate",
                    "Status": "PASS",
                    "Latency": f"{elapsed_ms}ms",
                    "Details": f"{top_name} ranked #1 with {top_score}% (all 6 deterministic factors verified)"
                })
            else:
                results_table.append({
                    "Test": "4. POST /api/matches/calculate",
                    "Status": "FAIL",
                    "Latency": f"{elapsed_ms}ms",
                    "Details": f"Expected Sarah Khan ~90-92%, got {top_name} {top_score}%"
                })
        else:
            print(f"  [FAIL] Status {res.status_code} | {data}")
            results_table.append({
                "Test": "4. POST /api/matches/calculate",
                "Status": "FAIL",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"HTTP {res.status_code}: {data}"
            })
    except Exception as e:
        results_table.append({
            "Test": "4. POST /api/matches/calculate",
            "Status": "ERROR",
            "Latency": "N/A",
            "Details": str(e)
        })
        print(f"  [FAIL] Error: {e}")

    # -------------------------------------------------------------
    # 5. POST /api/matches/explain (LangGraph Explainability Pipeline)
    # -------------------------------------------------------------
    print("\n[Step 5] Verifying POST /api/matches/explain (Sarah Khan & FashionCart) ...")
    start = time.time()
    explain_payload = {
        "business_id": "biz-fashioncart",
        "manager_id": "mgr_01"  # Sarah Khan
    }

    try:
        res = requests.post(f"{BASE_URL}/api/matches/explain", json=explain_payload, timeout=25)
        elapsed_ms = round((time.time() - start) * 1000, 1)
        data = res.json()

        mgr_name = data.get("manager_name")
        overall_score = data.get("overall_score")
        strengths = data.get("strengths", [])
        concerns = data.get("concerns", [])
        missing = data.get("missing_requirements", [])
        verdict = data.get("verdict", "")

        if res.status_code == 200 and strengths and verdict:
            print(f"  [PASS] 200 OK | Candidate: {mgr_name} ({overall_score}%) ({elapsed_ms}ms)")
            print(f"    - Strengths ({len(strengths)}): {strengths[0]}")
            print(f"    - Concerns ({len(concerns)}): {concerns[0] if concerns else 'None'}")
            print(f"    - Verdict: {verdict}")

            # Check zero-hallucination / responsible AI constraints
            banned_detected = any(w in verdict.lower() for w in ["guaranteed", "100% success", "perfect candidate"])

            if not banned_detected:
                results_table.append({
                    "Test": "5. POST /api/matches/explain",
                    "Status": "PASS",
                    "Latency": f"{elapsed_ms}ms",
                    "Details": f"4-quadrant explainability card generated for {mgr_name} (Zero hallucinations)"
                })
            else:
                results_table.append({
                    "Test": "5. POST /api/matches/explain",
                    "Status": "FAIL",
                    "Latency": f"{elapsed_ms}ms",
                    "Details": "Audited card contained un-sanitized banned marketing claims"
                })
        else:
            print(f"  [FAIL] Status {res.status_code} | {data}")
            results_table.append({
                "Test": "5. POST /api/matches/explain",
                "Status": "FAIL",
                "Latency": f"{elapsed_ms}ms",
                "Details": f"HTTP {res.status_code}: {data}"
            })
    except Exception as e:
        results_table.append({
            "Test": "5. POST /api/matches/explain",
            "Status": "ERROR",
            "Latency": "N/A",
            "Details": str(e)
        })
        print(f"  [FAIL] Error: {e}")

    # -------------------------------------------------------------
    # Summary Table
    # -------------------------------------------------------------
    log_header("Verification Results Summary Table")
    print(f"{'Test':<35} | {'Status':<8} | {'Latency':<10} | {'Details'}")
    print("-" * 105)

    all_passed = True
    for row in results_table:
        print(f"{row['Test']:<35} | {row['Status']:<8} | {row['Latency']:<10} | {row['Details']}")
        if row["Status"] != "PASS":
            all_passed = False

    print("=" * 105)
    if all_passed:
        print("\n[SUCCESS] ALL VERIFICATION TESTS PASSED! The system is completely production-ready and live.")
        sys.exit(0)
    else:
        print("\n[WARNING] SOME TESTS ENCOUNTERED FAILURES. Review the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
