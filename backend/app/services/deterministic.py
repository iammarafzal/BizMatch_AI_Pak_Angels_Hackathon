from typing import List, Dict, Any
from app.models.business import Business
from app.models.manager import Manager
from app.engine.matcher import (
    calculate_match,
    rank_managers_for_business,
    MatchResult
)

class ScoringEngine:
    """Service wrapper around the pure Python deterministic matching engine."""

    async def compute_matches_for_business(
        self, 
        business: Business, 
        managers: List[Manager], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        ranked_results: List[MatchResult] = rank_managers_for_business(business, managers, limit=limit)
        
        # Format for API route consumption
        return [
            {
                "manager": r.manager,
                "overall_score": r.overall_score,
                "factor_scores": {
                    "industry": r.factor_scores["industry_fit"],
                    "skills": r.factor_scores["skills_fit"],
                    "experience": r.factor_scores["experience_fit"],
                    "leadership": r.factor_scores["leadership_fit"],
                    "stage": r.factor_scores["stage_fit"],
                    "budget": r.factor_scores["salary_fit"],
                }
            }
            for r in ranked_results
        ]
