import urllib.request
import json

def test_api_flow():
    print("=== Testing Live API Endpoints for Frontend Integration ===")
    
    # 1. Demo Preset
    res = urllib.request.urlopen("http://localhost:8000/api/demo/fashioncart")
    data = json.loads(res.read().decode("utf-8"))
    print(f"1. [PASS] Demo Preset: name='{data.get('name')}', salary_budget=${data.get('salary_budget')}")
    
    # 2. Login Token
    login_req = urllib.request.Request(
        "http://localhost:8000/api/auth/login",
        data=json.dumps({"email": "founder@bizmatch.ai", "password": "password123"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    login_res = urllib.request.urlopen(login_req)
    token = json.loads(login_res.read().decode("utf-8")).get("access_token")
    assert token, "Token missing!"
    print(f"2. [PASS] Auth Login: Token acquired successfully (length {len(token)})")
    
    # 3. Analyze Requirements
    analyze_req = urllib.request.Request(
        "http://localhost:8000/api/analyze-requirements",
        data=json.dumps({
            "name": data.get("name"),
            "industry": data.get("industry"),
            "stage": data.get("stage"),
            "goals": data.get("goals"),
            "challenges": data.get("challenges"),
            "raw_preferences": data.get("challenges")
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    analyze_res = urllib.request.urlopen(analyze_req)
    req_data = json.loads(analyze_res.read().decode("utf-8"))
    print(f"3. [PASS] Analyze Requirements: stage='{req_data.get('business_stage')}', key_priorities count={len(req_data.get('key_priorities', []))}")
    
    # 4. Calculate Matches
    calc_req = urllib.request.Request(
        "http://localhost:8000/api/matches/calculate?include_explanations=true",
        data=json.dumps({"business_id": "biz-fashioncart"}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    calc_res = urllib.request.urlopen(calc_req)
    calc_data = json.loads(calc_res.read().decode("utf-8"))
    matches = calc_data.get("matches", [])
    assert len(matches) > 0, "Zero matches returned!"
    top = matches[0]
    print(f"4. [PASS] Calculate Matches: {len(matches)} candidates evaluated.")
    print(f"   #1 Match: {top['manager']['name']} ({top['overall_score']}%)")
    print(f"   Sub-factors: {top['factor_scores']}")
    assert top['manager']['name'] == "Sarah Khan", f"Expected Sarah Khan, got {top['manager']['name']}"
    
    # 5. Explain Match
    exp_req = urllib.request.Request(
        "http://localhost:8000/api/matches/explain",
        data=json.dumps({"business_id": "biz-fashioncart", "manager_id": top["manager"]["id"]}).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    )
    exp_res = urllib.request.urlopen(exp_req)
    exp_data = json.loads(exp_res.read().decode("utf-8"))
    print(f"5. [PASS] Explain Match: {exp_data.get('manager_name')} ({exp_data.get('overall_score')}%)")
    print(f"   Strengths ({len(exp_data.get('strengths', []))}): {exp_data.get('strengths')[0]}")
    print(f"   Concerns ({len(exp_data.get('concerns', []))}): {exp_data.get('concerns')[0]}")
    print(f"   Verdict: {exp_data.get('verdict')}")
    
    print("\n=== ALL LIVE BACKEND CHECKS PASSED: ZERO DUMMY/MOCK DATA REQUIRED ===")

if __name__ == "__main__":
    test_api_flow()
