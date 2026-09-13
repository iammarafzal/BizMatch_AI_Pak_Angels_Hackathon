import os
import sys
import json
from dataclasses import dataclass
from typing import List, Optional

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine.matcher import (
    calculate_industry_fit,
    calculate_skills_fit,
    calculate_experience_fit,
    calculate_leadership_fit,
    calculate_stage_fit,
    calculate_salary_fit,
    calculate_match,
    rank_managers_for_business,
    MatchResult
)

@dataclass
class MockBusiness:
    id: str
    name: str
    industry: str
    stage: str
    employee_count: int
    salary_budget: float
    required_skills: List[str]
    goals: Optional[str] = ""
    challenges: Optional[str] = ""

@dataclass
class MockManager:
    id: str
    name: str
    title: str
    years_experience: float
    industries: List[str]
    skills: List[str]
    previous_roles: List[str]
    management_experience: str
    leadership_score: float
    achievements: List[str]
    salary_expectation: float
    availability: str = "Available"
    location: str = "Remote"
    work_preference: str = "Remote/Hybrid"

def load_fixtures():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    with open(os.path.join(data_dir, "businesses.json"), "r", encoding="utf-8") as f:
        biz_data = json.load(f)
    with open(os.path.join(data_dir, "managers.json"), "r", encoding="utf-8") as f:
        mgr_data = json.load(f)

    bizs = [MockBusiness(**{k: v for k, v in b.items() if k in MockBusiness.__annotations__}) for b in biz_data]
    mgrs = [MockManager(**{k: v for k, v in m.items() if k in MockManager.__annotations__}) for m in mgr_data]
    return bizs, mgrs

def test_factor_scores_bounded():
    """Verify all 6 factor scores fall strictly within [0.0, 100.0]."""
    print("\n[TEST] Verifying factor scores are strictly bounded [0.0, 100.0]...")
    bizs, mgrs = load_fixtures()
    
    for b in bizs:
        for m in mgrs:
            ind_score = calculate_industry_fit(b.industry, m.industries)
            skills_score = calculate_skills_fit(b.required_skills, m.skills)
            exp_score = calculate_experience_fit(b, m)
            lead_score = calculate_leadership_fit(b, m)
            stage_score = calculate_stage_fit(b.stage, m)
            sal_score = calculate_salary_fit(b.salary_budget, m.salary_expectation)

            for name, score in [
                ("industry", ind_score),
                ("skills", skills_score),
                ("experience", exp_score),
                ("leadership", lead_score),
                ("stage", stage_score),
                ("salary", sal_score)
            ]:
                assert 0.0 <= score <= 100.0, f"Score out of bounds for {m.name} in {name}: {score}"

    print("[PASS] All factor scores across all fixture permutations fall within [0.0, 100.0].")

def test_weighted_formula_accuracy():
    """Verify overall weighted score strictly adheres to the 6-factor formula."""
    print("\n[TEST] Verifying weighted formula accuracy...")
    bizs, mgrs = load_fixtures()
    fc = [b for b in bizs if b.name == "FashionCart"][0]

    for m in mgrs:
        result = calculate_match(fc, m)
        fs = result.factor_scores
        
        expected = (
            (0.20 * fs["industry_fit"]) +
            (0.25 * fs["skills_fit"]) +
            (0.20 * fs["experience_fit"]) +
            (0.15 * fs["leadership_fit"]) +
            (0.10 * fs["stage_fit"]) +
            (0.10 * fs["salary_fit"])
        )
        assert abs(result.overall_score - round(expected, 1)) <= 0.1, (
            f"Overall score mismatch for {m.name}: expected {round(expected, 1)}, got {result.overall_score}"
        )

    print("[PASS] Weighted formula accurately matches overall score for all candidates.")

def test_salary_soft_penalties():
    """Verify candidates slightly above budget are degraded gracefully, not zeroed out."""
    print("\n[TEST] Verifying salary soft degradation penalties...")
    budget = 2000.0

    # Under budget or equal
    assert calculate_salary_fit(budget, 1800.0) == 100.0
    assert calculate_salary_fit(budget, 2000.0) == 100.0

    # 10% over budget ($2,200) -> should be 80.0 to 90.0
    score_10 = calculate_salary_fit(budget, 2200.0)
    assert 80.0 <= score_10 <= 90.0, f"Expected 80-90 for 10% over, got {score_10}"

    # 15% over budget ($2,300) -> should be 75.0 to 85.0
    score_15 = calculate_salary_fit(budget, 2300.0)
    assert 75.0 <= score_15 <= 85.0, f"Expected 75-85 for 15% over, got {score_15}"

    # 30% over budget ($2,600) -> should be 50.0 to 65.0
    score_30 = calculate_salary_fit(budget, 2600.0)
    assert 50.0 <= score_30 <= 65.0, f"Expected 50-65 for 30% over, got {score_30}"

    # Significantly over budget ($3,500) -> soft floor, NOT zero
    score_high = calculate_salary_fit(budget, 3500.0)
    assert score_high > 0.0, f"Expected non-zero soft floor for high salary, got {score_high}"

    print(f"[PASS] Salary degradation: 0% over={100.0}, 10% over={score_10}, 15% over={score_15}, 30% over={score_30}, 75% over={score_high}")

def test_fashioncart_benchmark_ranking():
    """
    Verify FashionCart demo benchmark ranking:
    - Sarah Khan ranks #1 (~90–92%)
    - Maria James ranks #2 (~82–86%)
    - Ali Ahmed ranks lower on salary/stage fit despite high experience (~70–78%)
    """
    print("\n[TEST] Verifying FashionCart benchmark ranking order...")
    bizs, mgrs = load_fixtures()
    fc = [b for b in bizs if b.name == "FashionCart"][0]

    ranked = rank_managers_for_business(fc, mgrs, limit=10)
    names_ranked = [r.manager.name for r in ranked]
    scores_by_name = {r.manager.name: r.overall_score for r in ranked}

    print("\nTop 5 Candidates for FashionCart:")
    for idx, r in enumerate(ranked[:5], 1):
        print(f"  #{idx}: {r.manager.name} — Overall Score: {r.overall_score}%")
        for factor, val in r.factor_scores.items():
            print(f"       - {factor}: {val}")

    # Benchmark 1: Sarah Khan ranks #1
    assert names_ranked[0] == "Sarah Khan", f"Expected Sarah Khan at #1, got {names_ranked[0]}"
    sarah_score = scores_by_name["Sarah Khan"]
    assert 88.0 <= sarah_score <= 95.0, f"Sarah Khan score out of benchmark range (~90-92%): {sarah_score}"

    # Benchmark 2: Maria James ranks #2
    assert names_ranked[1] == "Maria James", f"Expected Maria James at #2, got {names_ranked[1]}"
    maria_score = scores_by_name["Maria James"]
    assert 81.0 <= maria_score <= 88.0, f"Maria James score out of benchmark range (~82-86%): {maria_score}"

    # Benchmark 3: Ali Ahmed ranks lower (~70-78%)
    assert "Ali Ahmed" in scores_by_name, "Ali Ahmed should be present in top evaluated pool"
    ali_score = scores_by_name["Ali Ahmed"]
    assert 68.0 <= ali_score <= 78.0, f"Ali Ahmed score out of benchmark range (~70-78%): {ali_score}"
    assert ali_score < maria_score < sarah_score, (
        f"Ranking order incorrect: Sarah ({sarah_score}) > Maria ({maria_score}) > Ali ({ali_score})"
    )

    print(f"\n[PASS] Benchmark verified: Sarah Khan ({sarah_score}%) > Maria James ({maria_score}%) > Ali Ahmed ({ali_score}%)")

def run_all_tests():
    test_factor_scores_bounded()
    test_weighted_formula_accuracy()
    test_salary_soft_penalties()
    test_fashioncart_benchmark_ranking()
    print("\n=======================================================")
    print("ALL MATCHER UNIT TESTS PASSED SUCCESSFULLY (PURE PYTHON)")
    print("=======================================================\n")

if __name__ == "__main__":
    run_all_tests()
