from app.models.business import Business
from app.models.manager import Manager

# Stage progression logic
STAGE_ADJACENCY = {
    "Early/Idea": ["Early/Idea", "Seed"],
    "Seed": ["Early/Idea", "Seed", "Growth"],
    "Growth": ["Seed", "Growth", "Scale"],
    "Scale": ["Growth", "Scale"]
}

class ScoringEngine:
    def _calculate_stage_score(self, business_stage: str, manager_stages: list[str]) -> float:
        if not manager_stages:
            return 0.5
        if business_stage in manager_stages:
            return 1.0
        
        allowed_adjacent = STAGE_ADJACENCY.get(business_stage, [])
        if any(stage in manager_stages for stage in allowed_adjacent):
            return 0.7
        return 0.4

    def _calculate_skills_score(self, required_skills: list[str], manager_skills: list[str]) -> float:
        if not required_skills:
            return 0.5
        req_set = set(skill.lower() for skill in required_skills)
        mgr_set = set(skill.lower() for skill in manager_skills)
        
        matched = req_set.intersection(mgr_set)
        if not req_set:
            return 0.5
        return round(len(matched) / len(req_set), 2)

    def _calculate_industry_score(self, business_industry: str, manager_industries: list[str]) -> float:
        if not business_industry or not manager_industries:
            return 0.3
        
        b_ind = business_industry.lower()
        if any(m_ind.lower() == b_ind for m_ind in manager_industries):
            return 1.0
        return 0.3

    def _calculate_budget_score(self, business_budget: float, manager_rate: float) -> float:
        if business_budget <= 0 or manager_rate <= 0:
            return 0.5
        if manager_rate <= business_budget:
            return 1.0
        elif manager_rate <= business_budget * 1.15:
            return 0.75
        elif manager_rate <= business_budget * 1.30:
            return 0.40
        else:
            return 0.0

    async def compute_matches_for_business(self, business: Business, managers: list[Manager], limit: int = 10) -> list[dict]:
        ranked = []
        for m in managers:
            stages = getattr(m, "verified_stages", None) or getattr(m, "industries", []) or []
            skills = getattr(m, "skills", None) or getattr(m, "core_skills", []) or []
            industries = getattr(m, "industries", []) or []
            
            budget = getattr(business, "salary_budget", None)
            if budget is None:
                budget = getattr(business, "monthly_budget_usd", 0)
                
            rate = getattr(m, "salary_expectation", None)
            if rate is None:
                rate = getattr(m, "monthly_rate_usd", 0)
            
            req_skills = getattr(business, "required_skills", []) or []

            s_stage = self._calculate_stage_score(business.stage or "Growth", stages)
            s_skills = self._calculate_skills_score(req_skills, skills)
            s_ind = self._calculate_industry_score(business.industry or "", industries)
            s_budget = self._calculate_budget_score(float(budget or 0), float(rate or 0))
            
            # Weighted calculation
            w_stage, w_skills, w_ind, w_budget = 0.25, 0.35, 0.20, 0.20
            
            total_score = 100 * (
                (w_stage * s_stage) +
                (w_skills * s_skills) +
                (w_ind * s_ind) +
                (w_budget * s_budget)
            )
            
            ranked.append({
                "manager": m,
                "overall_score": round(total_score, 2),
                "factor_scores": {
                    "stage": round(s_stage * 100, 2),
                    "skills": round(s_skills * 100, 2),
                    "industry": round(s_ind * 100, 2),
                    "budget": round(s_budget * 100, 2)
                }
            })
            
        ranked.sort(key=lambda x: x["overall_score"], reverse=True)
        return ranked[:limit]
