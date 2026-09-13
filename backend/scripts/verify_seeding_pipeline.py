import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_seeding_pipeline():
    print("=" * 70)
    print("BIZMATCH AI - DATABASE SEEDING & ENDPOINTS VERIFICATION")
    print("=" * 70)

    # 1. Verify GET /api/demo/fashioncart
    print("\n[TEST 1] GET /api/demo/fashioncart")
    res_demo = requests.get(f"{BASE_URL}/api/demo/fashioncart")
    assert res_demo.status_code == 200, f"Demo endpoint failed: {res_demo.status_code} {res_demo.text}"
    demo_data = res_demo.json()
    name = demo_data.get("name")
    industry = demo_data.get("industry")
    budget = demo_data.get("salary_budget")
    print(f"  -> Status: {res_demo.status_code}")
    print(f"  -> Business Name: {name}")
    print(f"  -> Industry: {industry}")
    print(f"  -> Salary Budget: ${budget}/mo")
    assert name == "FashionCart", f"Expected FashionCart, got {name}"
    assert industry in ["Fashion E-commerce", "E-commerce"], f"Expected Fashion E-commerce or E-commerce, got {industry}"
    assert budget == 2000, f"Expected 2000, got {budget}"
    print("  -> PASS: Demo scenario delivered cleanly from backend.")

    # 2. Verify GET /api/managers
    print("\n[TEST 2] GET /api/managers")
    res_mgrs = requests.get(f"{BASE_URL}/api/managers")
    assert res_mgrs.status_code == 200, f"Managers endpoint failed: {res_mgrs.status_code}"
    mgrs = res_mgrs.json()
    print(f"  -> Status: {res_mgrs.status_code}")
    print(f"  -> Total Managers Count: {len(mgrs)}")
    assert len(mgrs) >= 15, f"Expected at least 15 managers, got {len(mgrs)}"
    
    first_mgr = mgrs[0]
    print(f"  -> First candidate: {first_mgr['name']} ({first_mgr['title']}) - ID: {first_mgr['id']}")
    print("  -> PASS: All seeded manager profiles returned with 200 OK.")

    # 3. Verify GET /api/managers/mgr_01 and alias /api/managers/mgr-sarah-khan
    print("\n[TEST 3] GET /api/managers/mgr_01")
    res_s1 = requests.get(f"{BASE_URL}/api/managers/mgr_01")
    assert res_s1.status_code == 200, f"mgr_01 failed: {res_s1.status_code}"
    s1 = res_s1.json()
    print(f"  -> Name: {s1['name']}, Title: {s1['title']}, Rate: ${s1['salary_expectation']}/mo")
    assert s1["name"] == "Sarah Khan", f"Expected Sarah Khan, got {s1['name']}"

    print("\n[TEST 4] GET /api/managers/mgr-sarah-khan (Alias verification)")
    res_s2 = requests.get(f"{BASE_URL}/api/managers/mgr-sarah-khan")
    assert res_s2.status_code == 200, f"mgr-sarah-khan alias failed: {res_s2.status_code}"
    s2 = res_s2.json()
    print(f"  -> Alias resolved successfully to: {s2['name']} (ID: {s2['id']})")
    assert s2["name"] == "Sarah Khan"
    print("  -> PASS: Both canonical ID and slug alias resolve identically.")

    # 4. Authenticate for deterministic calculate & explain endpoints
    print("\n[TEST 5] Authenticate demo user (founder@bizmatch.ai)")
    auth_res = requests.post(f"{BASE_URL}/api/auth/login", data={"username": "founder@bizmatch.ai", "password": "password123"})
    if auth_res.status_code != 200:
        # Try JSON body format
        auth_res = requests.post(f"{BASE_URL}/api/auth/login", json={"email": "founder@bizmatch.ai", "password": "password123"})
    assert auth_res.status_code == 200, f"Auth failed: {auth_res.text}"
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("  -> Bearer JWT token acquired successfully.")

    # 5. Verify POST /api/matches/calculate with seeded FashionCart business
    print("\n[TEST 6] POST /api/matches/calculate")
    calc_res = requests.post(
        f"{BASE_URL}/api/matches/calculate",
        json={"business_id": "biz-fashioncart"},
        headers=headers
    )
    assert calc_res.status_code == 200, f"Calculate matches failed: {calc_res.text}"
    calc_data = calc_res.json()
    matches = calc_data.get("matches", [])
    print(f"  -> Total Evaluated Matches: {calc_data.get('total_evaluated', len(matches))}")
    assert len(matches) > 0, "No matches returned!"

    top_match = matches[0]
    top_name = top_match["manager"]["name"]
    top_score = top_match["overall_score"]
    print(f"  -> #1 Ranked Manager: {top_name} with {top_score:.1f}% fit score")
    assert "Sarah Khan" in top_name, f"Expected Sarah Khan to rank #1, got {top_name}"
    print("  -> PASS: Deterministic ranking verified with Sarah Khan as #1!")

    # 6. Verify POST /api/matches/explain
    print("\n[TEST 7] POST /api/matches/explain")
    exp_res = requests.post(
        f"{BASE_URL}/api/matches/explain",
        json={"business_id": "biz-fashioncart", "manager_id": "mgr_01"},
        headers=headers
    )
    assert exp_res.status_code == 200, f"Explain endpoint failed: {exp_res.text}"
    exp_data = exp_res.json()
    data_payload = exp_data.get("data", exp_data)
    verdict = data_payload.get("verdict", "")
    strengths = data_payload.get("strengths", [])
    print(f"  -> Strengths identified: {len(strengths)}")
    print(f"  -> Strategic Verdict: {verdict[:100]}...")
    assert len(strengths) > 0, "Expected strengths in explanation card"
    assert len(verdict) > 0, "Expected strategic verdict"
    print("  -> PASS: Explainability card generated successfully from seeded database.")

    print("\n" + "=" * 70)
    print("ALL 7 TESTS PASSED! Automatic seeding pipeline is 100% operational.")
    print("=" * 70)

if __name__ == "__main__":
    test_seeding_pipeline()
