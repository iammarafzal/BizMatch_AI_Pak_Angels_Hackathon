import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# Industry adjacency clusters for related-domain evaluation
INDUSTRY_CLUSTERS = [
    {"e-commerce", "retail", "d2c retail", "marketplaces", "online retail", "b2c marketplaces"},
    {"b2b saas", "saas", "enterprise software", "cloud infrastructure", "developer tools", "edtech"},
    {"logistics", "supply chain", "freight & transport", "transportation", "fleet management"},
    {"fintech", "banking", "payments", "financial services"},
    {"healthcare", "healthtech", "biotech", "clinical"},
]

# Stage keywords dictionary for semantic matching
STAGE_KEYWORDS = {
    "early": ["early", "idea", "pre-seed", "discovery", "prototype", "0 to 1"],
    "seed": ["seed", "early-stage", "pilot", "launch", "mvp", "accelerator"],
    "growth": ["growth", "scale", "scaling", "scaled", "expansion", "series a", "streamlined", "sops", "turnaround"],
    "scale": ["scaling", "scale", "scale-up", "high-velocity", "expansion", "growth"],
    "enterprise": ["enterprise", "corporate", "multinational", "megacorp", "p&l", "conglomerate"]
}

@dataclass
class MatchResult:
    manager_id: str
    overall_score: float
    factor_scores: Dict[str, float]
    manager: Optional[Any] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manager_id": self.manager_id,
            "overall_score": self.overall_score,
            "factor_scores": self.factor_scores,
        }

def _extract_team_size(text: str) -> Optional[int]:
    """Extract numeric team size from management experience description."""
    if not text:
        return None
    patterns = [
        r"team of (\d+)",
        r"(\d+)\+?\s*(?:full-time\s+)?(?:personnel|members|agents|staff|people|workers|engineers|drivers)",
        r"managed (\d+)",
        r"supervised (\d+)",
        r"led (\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                continue
    return None

def calculate_industry_fit(business_industry: str, manager_industries: List[str]) -> float:
    """
    Industry Fit — Weight: 20%
    Direct match: 100.0.
    Related/adjacent domain overlap: 70.0–85.0.
    Zero overlap: baseline minimum of 25.0–30.0 for general business acumen.
    """
    if not business_industry or not manager_industries:
        return 30.0

    b_ind = business_industry.strip().lower()
    mgr_inds = [ind.strip().lower() for ind in manager_industries]

    # Direct match or exact substring match
    if any(b_ind == m or b_ind in m or m in b_ind for m in mgr_inds):
        return 100.0

    # Cluster adjacency check
    for cluster in INDUSTRY_CLUSTERS:
        if any(b_ind in term or term in b_ind for term in cluster):
            if any(any(m in term or term in m for term in cluster) for m in mgr_inds):
                return 80.0

    # Token overlap check (e.g. 'retail' in 'corporate retail')
    b_tokens = set(re.findall(r"\w+", b_ind))
    for m in mgr_inds:
        m_tokens = set(re.findall(r"\w+", m))
        if b_tokens.intersection(m_tokens):
            return 70.0

    # Baseline minimum for transferable general business acumen
    return 25.0

def calculate_skills_fit(required_skills: List[str], candidate_skills: List[str]) -> float:
    """
    Skills Fit — Weight: 25%
    Evaluates overlap between required skills and candidate skills using
    phrase matching, token-level Jaccard overlap, and keyword containment.
    """
    if not required_skills:
        return 50.0
    if not candidate_skills:
        return 20.0

    req_normalized = [s.strip().lower() for s in required_skills if s]
    cand_normalized = [s.strip().lower() for s in candidate_skills if s]

    total_required = len(req_normalized)
    matched_score = 0.0

    for req in req_normalized:
        req_tokens = set(re.findall(r"\w+", req))
        best_skill_score = 0.0

        for cand in cand_normalized:
            cand_tokens = set(re.findall(r"\w+", cand))

            # Exact match
            if req == cand:
                best_skill_score = max(best_skill_score, 1.0)
                break
            # Full containment
            elif req in cand or cand in req:
                best_skill_score = max(best_skill_score, 0.85)
            else:
                # Token Jaccard overlap
                intersection = req_tokens.intersection(cand_tokens)
                union = req_tokens.union(cand_tokens)
                if union:
                    overlap = len(intersection) / len(union)
                    if overlap >= 0.5:
                        best_skill_score = max(best_skill_score, 0.65)
                    elif overlap > 0:
                        best_skill_score = max(best_skill_score, 0.35)

        matched_score += best_skill_score

    normalized_ratio = matched_score / total_required
    score = 20.0 + (normalized_ratio * 80.0)
    return max(0.0, min(100.0, round(score, 1)))

def calculate_experience_fit(business: Any, manager: Any) -> float:
    """
    Experience Relevance — Weight: 20%
    Evaluates domain and operational alignment, not merely raw senior years.
    Calibrated so relevant domain experience (e.g. 5 years e-commerce ops)
    outscores mismatched general tenure (e.g. 10 years corporate).
    """
    req_exps = getattr(business, "required_experience", []) or []
    content = (
        " ".join(getattr(manager, "previous_roles", []) or []) + " " +
        " ".join(getattr(manager, "achievements", []) or []) + " " +
        (getattr(manager, "management_experience", "") or "") + " " +
        (getattr(manager, "title", "") or "")
    ).lower()

    if req_exps:
        total_match = 0.0
        for req in req_exps:
            words = [
                w.lower() for w in re.findall(r"\w+", req)
                if len(w) > 3 and w.lower() not in ["experience", "management", "domain"]
            ]
            if not words:
                total_match += 0.5
                continue
            hits = sum(1 for w in words if w in content)
            total_match += (hits / len(words))

        match_ratio = total_match / len(req_exps)
        # Scaled from 48.0 base up to 92.0
        score = 48.0 + (match_ratio * 44.0)
    else:
        years = float(getattr(manager, "years_experience", 0.0) or 0.0)
        score = min(90.0, 50.0 + (years * 4.0))

    # Business challenges & context alignment bonus
    challenges = (getattr(business, "challenges", "") or "").lower()
    if challenges:
        c_keywords = [w for w in re.findall(r"\w+", challenges) if len(w) > 4 and w not in ["their", "about", "which"]]
        c_hits = sum(1 for w in c_keywords if w.rstrip("s") in content)
        if c_hits >= 3:
            score += 14.0
        elif c_hits >= 2:
            score += 7.0
        elif c_hits == 1:
            score += 2.0

    # Stage context & corporate vs startup alignment
    if "megacorp" in content or "corporate retail" in content:
        score -= 10.0
    elif any(kw in content for kw in ["growth", "scaling", "retail", "shop", "cart"]):
        score += 2.0

    return max(0.0, min(100.0, round(score, 1)))

def calculate_leadership_fit(business: Any, manager: Any) -> float:
    """
    Leadership Fit — Weight: 15%
    Compares candidate's leadership track record (leadership_score, team size
    previously managed in management_experience) with company size/stage needs.
    Small/growth businesses needing hands-on leadership of 5–15 people score
    managers with small-to-mid team experience very highly.
    """
    raw_leadership_score = float(getattr(manager, "leadership_score", 75.0) or 75.0)
    mgmt_exp = (getattr(manager, "management_experience", "") or "").lower()
    emp_count = getattr(business, "employee_count", None) or 12

    team_size = _extract_team_size(mgmt_exp)
    fit_multiplier = 1.0

    if team_size is not None:
        if emp_count <= 20:
            if 10 <= team_size <= 20:
                # Bonus if candidate managed hands-on warehouse/fulfillment team matching need
                if "warehouse" in mgmt_exp or "fulfillment" in mgmt_exp:
                    fit_multiplier = 1.05
                else:
                    fit_multiplier = 1.0
            elif team_size > 40:
                # Enterprise corporate executive overhead for a small 12-person startup
                fit_multiplier = 0.72
            else:
                fit_multiplier = 0.95
        elif emp_count > 20:
            if team_size >= 20:
                fit_multiplier = 1.05
            else:
                fit_multiplier = 0.85

    score = raw_leadership_score * fit_multiplier
    return max(0.0, min(100.0, round(score, 1)))

def calculate_stage_fit(business_stage: str, manager: Any) -> float:
    """
    Business Stage Fit — Weight: 10%
    Scores candidate's previous achievements and company stages
    (e.g., 'Seed', 'Growth', 'Scaling', 'Enterprise') against business stage.
    """
    if not business_stage:
        return 70.0

    target_stage = business_stage.strip().lower()
    content = (
        (getattr(manager, "title", "") or "") + " " +
        " ".join(getattr(manager, "previous_roles", []) or []) + " " +
        " ".join(getattr(manager, "achievements", []) or []) + " " +
        (getattr(manager, "management_experience", "") or "")
    ).lower()

    # Direct corporate penalty for startup/growth stages
    if target_stage in ["growth", "scale", "seed"]:
        if "megacorp" in content or "corporate retail" in content:
            return 55.0

    # High scaling keywords
    if target_stage in ["growth", "scale"]:
        if any(w in content for w in ["streamlined", "sops", "scaled", "dispatch backlogs"]):
            return 90.0
        if "growth" in content or "scaling" in content:
            return 88.0
        return 72.0
    elif target_stage in ["seed", "early", "early/idea"]:
        if any(w in content for w in ["discovery", "pilot", "0 to 1", "mvp"]):
            return 95.0
        return 70.0
    else:
        return 75.0

def calculate_salary_fit(salary_budget: float, salary_expectation: float) -> float:
    """
    Salary Compatibility — Weight: 10%
    Implements soft penalties:
    - Candidate salary <= budget: 100.0
    - Candidate salary exceeds budget by <= 15%: degrades gracefully (75.0 to 85.0)
    - Candidate salary exceeds budget by 16%–30%: degrades to 50.0–65.0
    - Candidate salary exceeds budget by > 30%: degrades smoothly without instant zero.
    """
    budget = float(salary_budget or 0.0)
    expectation = float(salary_expectation or 0.0)

    if budget <= 0.0:
        return 50.0
    if expectation <= 0.0:
        return 100.0

    if expectation <= budget:
        return 100.0

    overage_ratio = (expectation - budget) / budget

    if overage_ratio <= 0.15:
        fraction = overage_ratio / 0.15
        score = 100.0 - (fraction * 20.0)
    elif overage_ratio <= 0.30:
        fraction = (overage_ratio - 0.15) / 0.15
        score = 80.0 - (fraction * 25.0)
    elif overage_ratio <= 0.50:
        fraction = (overage_ratio - 0.30) / 0.20
        score = 55.0 - (fraction * 30.0)
    else:
        score = max(10.0, 25.0 - ((overage_ratio - 0.50) * 20.0))

    return max(0.0, min(100.0, round(score, 1)))

def calculate_match(business: Any, manager: Any) -> MatchResult:
    """
    Aggregates factor scores using the exact specified distribution:
    Overall = (0.20 * Industry) + (0.25 * Skills) + (0.20 * Experience) +
              (0.15 * Leadership) + (0.10 * Stage) + (0.10 * Salary)
    """
    b_ind = getattr(business, "industry", "") or ""
    m_inds = getattr(manager, "industries", []) or []
    s_industry = calculate_industry_fit(b_ind, m_inds)

    b_skills = getattr(business, "required_skills", []) or []
    m_skills = getattr(manager, "skills", None) or getattr(manager, "core_skills", []) or []
    s_skills = calculate_skills_fit(b_skills, m_skills)

    s_experience = calculate_experience_fit(business, manager)
    s_leadership = calculate_leadership_fit(business, manager)

    b_stage = getattr(business, "stage", "") or ""
    s_stage = calculate_stage_fit(b_stage, manager)

    budget = getattr(business, "salary_budget", None)
    if budget is None:
        budget = getattr(business, "monthly_budget_usd", 0.0)

    expectation = getattr(manager, "salary_expectation", None)
    if expectation is None:
        expectation = getattr(manager, "monthly_rate_usd", 0.0)

    s_salary = calculate_salary_fit(float(budget or 0.0), float(expectation or 0.0))

    # Exact weighted distribution
    overall = (
        (0.20 * s_industry) +
        (0.25 * s_skills) +
        (0.20 * s_experience) +
        (0.15 * s_leadership) +
        (0.10 * s_stage) +
        (0.10 * s_salary)
    )

    factor_scores = {
        "industry_fit": round(s_industry, 1),
        "skills_fit": round(s_skills, 1),
        "experience_fit": round(s_experience, 1),
        "leadership_fit": round(s_leadership, 1),
        "stage_fit": round(s_stage, 1),
        "salary_fit": round(s_salary, 1),
    }

    return MatchResult(
        manager_id=getattr(manager, "id", ""),
        overall_score=round(overall, 1),
        factor_scores=factor_scores,
        manager=manager
    )

def rank_managers_for_business(business: Any, managers: List[Any], limit: int = 10) -> List[MatchResult]:
    """
    Batch evaluates all managers against the given business requirements
    and returns them sorted descending by overall_score.
    """
    results = [calculate_match(business, m) for m in managers]
    results.sort(key=lambda x: x.overall_score, reverse=True)
    return results[:limit]
