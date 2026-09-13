from __future__ import annotations
import os
import re
from typing import TypedDict, Dict, Any, Optional, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from app.core.config import settings
from app.schemas.explanation import MatchExplanation, ExplanationCard

# 1. Initialize Gemini Model
api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=api_key or "dummy_key",
    )
except Exception:
    llm = None


# 2. State Schema
class EvaluationState(TypedDict):
    business_profile: Dict[str, Any]
    manager_profile: Dict[str, Any]
    factor_scores: Dict[str, float]
    overall_score: float
    raw_explanation: MatchExplanation | None
    final_explanation: Dict[str, Any] | None


# 3. Deterministic Fallback Generator
def _generate_fallback_explanation(
    business: Dict[str, Any],
    manager: Dict[str, Any],
    factor_scores: Dict[str, float],
    overall_score: float
) -> MatchExplanation:
    """
    Generate an evidence-backed deterministic MatchExplanation when Gemini API
    is unreachable, unconfigured, or encounters quota/network exceptions.
    """
    manager_name = manager.get("name", "Candidate")
    role_title = manager.get("role_title") or manager.get("title", "Operations Manager")
    industries = manager.get("industries", [])
    skills = manager.get("skills", [])
    achievements = manager.get("achievements", [])
    expected_salary = float(manager.get("expected_salary", 0.0) or 0.0)
    
    biz_name = business.get("name", "the business")
    biz_industry = business.get("industry", "Target Industry")
    biz_stage = business.get("stage", "Growth")
    biz_budget = float(business.get("salary_budget", 0.0) or business.get("monthly_budget_usd", 0.0) or 0.0)
    required_skills = business.get("required_skills", [])

    # Strengths (2-4 items)
    strengths: List[str] = []
    
    # 1. Domain/Industry fit
    ind_overlap = [i for i in industries if i.lower() in biz_industry.lower() or biz_industry.lower() in i.lower()]
    if ind_overlap:
        strengths.append(
            f"Demonstrated domain experience in {', '.join(ind_overlap)}, directly aligning with {biz_name}'s market."
        )
    elif industries:
        strengths.append(
            f"Demonstrated operating track record across {', '.join(industries[:2])} providing transferable execution acumen."
        )
    else:
        strengths.append(
            f"Proven execution track record as {role_title} aligned with organizational scaling needs."
        )

    # 2. Skills fit
    matched_skills = [s for s in skills if any(req.lower() in s.lower() or s.lower() in req.lower() for req in required_skills)]
    if matched_skills:
        strengths.append(
            f"Hands-on expertise in {', '.join(matched_skills[:3])} directly addressing core operational bottlenecks."
        )
    elif skills:
        strengths.append(
            f"Strong competency in {', '.join(skills[:3])} supporting execution priorities."
        )
    else:
        strengths.append("Verified leadership background managing cross-functional teams.")

    # 3. Achievements / Track record
    if achievements:
        strengths.append(f"Documented milestone achievement: {achievements[0]}.")
    elif manager.get("experience_years"):
        strengths.append(
            f"{manager.get('experience_years')} years of progressive leadership experience navigating {biz_stage} challenges."
        )

    # Ensure strengths length between 2 and 4
    strengths = strengths[:4]
    while len(strengths) < 2:
        strengths.append(f"Verified profile credentials supporting operational growth for {biz_name}.")

    # Concerns / Trade-offs (1-3 items)
    concerns: List[str] = []
    
    # Salary trade-off
    if biz_budget > 0 and expected_salary > biz_budget:
        concerns.append(
            f"Expected salary of ${expected_salary:,.0f}/mo exceeds target budget (${biz_budget:,.0f}/mo); "
            "represents a compensation trade-off requiring milestone-based equity or bonus restructuring."
        )
    elif factor_scores.get("salary_fit", 100.0) < 80.0:
        concerns.append(
            f"Compensation expectations (${expected_salary:,.0f}/mo) sit near upper budget threshold."
        )

    # Stage / transition trade-off
    verified_stages = [s.lower() for s in manager.get("verified_stages", [])]
    if biz_stage.lower() not in verified_stages and verified_stages:
        concerns.append(
            f"Primary stage experience is concentrated in {', '.join(manager.get('verified_stages', [])[:2])}; "
            f"requires validating adaptability to {biz_stage} velocity."
        )
    else:
        concerns.append(
            "Verify remote/hybrid workflow cadences and alignment on weekly OKR tracking during onboarding."
        )

    concerns = concerns[:3]

    # Missing requirements
    mgr_skills_lower = [s.lower() for s in skills]
    missing: List[str] = []
    for req in required_skills:
        if not any(req.lower() in s or s in req.lower() for s in mgr_skills_lower):
            missing.append(req)

    # Recommendation verdict
    if overall_score >= 85.0:
        verdict = (
            f"Strongly recommended candidate with {overall_score:.1f}% match; possesses exceptional skill and stage "
            f"synergy for {biz_name}'s {biz_stage} trajectory, with minimal operational friction."
        )
    elif overall_score >= 70.0:
        verdict = (
            f"Solid candidate with {overall_score:.1f}% match; offers high domain competence with practical trade-offs "
            f"in compensation or tooling alignment that can be resolved via structured onboarding."
        )
    else:
        verdict = (
            f"Moderate candidate fit ({overall_score:.1f}% match); has notable leadership experience but requires "
            f"further evaluation regarding specific domain and budget trade-offs."
        )

    return MatchExplanation(
        strengths=strengths,
        concerns=concerns,
        missing_requirements=missing,
        recommendation_verdict=verdict
    )


# 4. Responsible AI & Hallucination Audit Helpers
BANNED_BUZZWORDS = ["guaranteed", "predicts", "guarantee", "100% success", "will definitely succeed", "perfect candidate"]

PROTECTED_CLASSES_PATTERNS = [
    (r"\b(\d+[\s-]*year[\s-]*old)\b", "experienced"),
    (r"\b(he\s+is|she\s+is)\b", "the candidate is"),
    (r"\b(he\s+has|she\s+has)\b", "the candidate has"),
    (r"\b(his|her)\b", "their"),
    (r"\b(him|her)\b", "them"),
    (r"\b(he|she)\b", "they"),
    (r"\b(male|female|woman|man)\b", "professional"),
    (r"\b(pakistani|american|asian|caucasian|black|white|muslim|christian|hindu|married|single)\b", ""),
]

def _sanitize_responsible_ai(text: str) -> str:
    """Strip or replace protected demographic attributes and banned buzzwords."""
    cleaned = text
    for pattern, replacement in PROTECTED_CLASSES_PATTERNS:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    for word in BANNED_BUZZWORDS:
        cleaned = re.sub(re.escape(word), "aligns with", cleaned, flags=re.IGNORECASE)
    # Clean up double spaces created by deletions
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned


def _build_candidate_ground_truth(manager: Dict[str, Any]) -> str:
    """Aggregate all verified facts from manager profile into a searchable corpus."""
    tokens = []
    tokens.append(str(manager.get("name", "")))
    tokens.append(str(manager.get("role_title", "")))
    tokens.append(str(manager.get("title", "")))
    tokens.extend(manager.get("skills", []))
    tokens.extend(manager.get("industries", []))
    tokens.extend([str(r) for r in manager.get("previous_roles", [])])
    tokens.extend([str(a) for a in manager.get("achievements", [])])
    tokens.extend(manager.get("verified_stages", []))
    tokens.append(str(manager.get("verified_track_record", "")))
    tokens.append(str(manager.get("bio", "")))
    return " ".join(tokens).lower()


# 5. Node 1: generate_explanation_node
async def generate_explanation_node(state: EvaluationState) -> Dict[str, Any]:
    """
    Generate initial MatchExplanation using Gemini 2.5 Flash with structured output.
    Strictly accepts deterministic factor scores as read-only inputs.
    """
    business = state["business_profile"]
    manager = state["manager_profile"]
    factor_scores = state["factor_scores"]
    overall_score = state["overall_score"]

    if not api_key or api_key in ("dummy_key", "test_key") or llm is None:
        explanation = _generate_fallback_explanation(business, manager, factor_scores, overall_score)
        return {"raw_explanation": explanation}

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an objective, fair executive hiring advisor for high-growth businesses and startups. "
            "Your role is to synthesize candidate suitability and articulate balanced decision-support evaluations.\n\n"
            "Crucial Guidelines:\n"
            "1. Never compute, adjust, or alter numerical match scores. All scores provided are deterministic read-only inputs.\n"
            "2. Ground every strength strictly in the candidate's verified profile data (actual skills, previous roles, achievements). Never fabricate certifications, past employers, or unlisted capabilities.\n"
            "3. Explain why the candidate fits the business stage and operational bottlenecks, citing concrete experience.\n"
            "4. Highlight realistic trade-offs and risks in 'concerns' (e.g., strong scaling background but limited international exposure, or high-velocity execution vs enterprise governance).\n"
            "5. If expected salary exceeds the business salary budget, frame it strictly as a compensation/budget trade-off (e.g. potential need for equity or bonus structure), NOT as an automatic dismissal.\n"
            "6. If required capabilities are absent from the candidate's profile, explicitly place them in 'missing_requirements'.\n"
            "7. Responsible AI: Strictly DO NOT mention, infer, or evaluate based on age, gender, race, religion, marital status, nationality, or any protected personal characteristics.\n"
            "8. Deliver a balanced 1-2 sentence recommendation verdict summarizing strategic fit and key trade-offs."
        ),
        (
            "human",
            "Business Context:\n"
            "- Name: {biz_name}\n"
            "- Industry: {biz_industry}\n"
            "- Stage: {biz_stage}\n"
            "- Budget: ${biz_budget}/month\n"
            "- Core Goals: {biz_goals}\n"
            "- Bottlenecks/Challenges: {biz_challenges}\n"
            "- Required Skills: {biz_skills}\n"
            "- Required Experience: {biz_experience}\n\n"
            "Candidate Profile:\n"
            "- Name: {mgr_name}\n"
            "- Role Title: {mgr_title}\n"
            "- Experience: {mgr_exp_years} years\n"
            "- Expected Salary: ${mgr_salary}/month\n"
            "- Industries: {mgr_industries}\n"
            "- Core Skills: {mgr_skills}\n"
            "- Previous Roles: {mgr_roles}\n"
            "- Achievements: {mgr_achievements}\n"
            "- Verified Stages: {mgr_stages}\n"
            "- Track Record: {mgr_track_record}\n\n"
            "Deterministic Match Scores (Read-Only):\n"
            "- Industry Fit: {ind_fit:.1f}/100\n"
            "- Skills Fit: {skills_fit:.1f}/100\n"
            "- Experience Fit: {exp_fit:.1f}/100\n"
            "- Leadership Fit: {lead_fit:.1f}/100\n"
            "- Stage Fit: {stage_fit:.1f}/100\n"
            "- Salary Fit: {salary_fit:.1f}/100\n"
            "- Overall Compatibility Score: {overall:.1f}/100\n\n"
            "Generate the structured MatchExplanation."
        )
    ])

    try:
        chain = prompt | llm.with_structured_output(MatchExplanation)
        result: MatchExplanation = await chain.ainvoke({
            "biz_name": business.get("name", "Startup"),
            "biz_industry": business.get("industry", "Technology"),
            "biz_stage": business.get("stage", "Growth"),
            "biz_budget": business.get("salary_budget") or business.get("monthly_budget_usd", 0.0),
            "biz_goals": business.get("goals", "Scale operations"),
            "biz_challenges": business.get("challenges", "Process bottlenecks"),
            "biz_skills": ", ".join(business.get("required_skills", [])),
            "biz_experience": ", ".join(business.get("required_experience", [])),
            "mgr_name": manager.get("name", "Candidate"),
            "mgr_title": manager.get("role_title") or manager.get("title", "Manager"),
            "mgr_exp_years": manager.get("experience_years", 0),
            "mgr_salary": manager.get("expected_salary", 0.0),
            "mgr_industries": ", ".join(manager.get("industries", [])),
            "mgr_skills": ", ".join(manager.get("skills", [])),
            "mgr_roles": str(manager.get("previous_roles", [])),
            "mgr_achievements": str(manager.get("achievements", [])),
            "mgr_stages": ", ".join(manager.get("verified_stages", [])),
            "mgr_track_record": manager.get("verified_track_record") or manager.get("bio", ""),
            "ind_fit": factor_scores.get("industry_fit", 0.0),
            "skills_fit": factor_scores.get("skills_fit", 0.0),
            "exp_fit": factor_scores.get("experience_fit", 0.0),
            "lead_fit": factor_scores.get("leadership_fit", 0.0),
            "stage_fit": factor_scores.get("stage_fit", 0.0),
            "salary_fit": factor_scores.get("salary_fit", 0.0),
            "overall": overall_score,
        })
        return {"raw_explanation": result}
    except Exception:
        # Resilient fallback on any LLM parsing or API exception
        fallback = _generate_fallback_explanation(business, manager, factor_scores, overall_score)
        return {"raw_explanation": fallback}


# 6. Node 2: audit_and_format_node
async def audit_and_format_node(state: EvaluationState) -> Dict[str, Any]:
    """
    Zero-hallucination verification and Responsible AI audit:
    1. Cross-checks claimed strengths against the candidate's actual profile facts.
    2. Flags or moves ungrounded claims to missing_requirements.
    3. Strips prohibited demographic references and banned marketing buzzwords.
    4. Structures clean payload for client consumption.
    """
    raw_exp = state.get("raw_explanation")
    manager = state["manager_profile"]
    business = state["business_profile"]

    if raw_exp is None:
        raw_exp = _generate_fallback_explanation(
            business, manager, state["factor_scores"], state["overall_score"]
        )

    ground_truth = _build_candidate_ground_truth(manager)
    required_skills = business.get("required_skills", [])

    cleaned_strengths: List[str] = []
    audited_missing = list(raw_exp.missing_requirements)

    for item in raw_exp.strengths:
        sanitized_item = _sanitize_responsible_ai(item)
        if not sanitized_item:
            continue

        # Zero-hallucination check: verify if the item falsely asserts domain/tool expertise
        # that is in required_skills but completely missing from ground truth
        hallucination_detected = False
        for req in required_skills:
            if req.lower() in sanitized_item.lower() and req.lower() not in ground_truth:
                hallucination_detected = True
                audited_missing.append(f"{req} (asserted in narrative but not verified in profile)")
                break

        if hallucination_detected:
            # Reassign or flag as unverified
            flagged = f"{sanitized_item} (Note: Specific domain experience not verified in profile)"
            cleaned_strengths.append(flagged)
        else:
            cleaned_strengths.append(sanitized_item)

    # Ensure strengths adhere to constraints (2-4 items)
    if len(cleaned_strengths) < 2:
        mgr_skills = manager.get("skills", [])
        if mgr_skills:
            cleaned_strengths.append(f"Demonstrated operational competence in {', '.join(mgr_skills[:2])}.")
        else:
            cleaned_strengths.append("Verified leadership background supporting business scaling milestones.")
    cleaned_strengths = cleaned_strengths[:4]

    # Sanitize concerns
    cleaned_concerns = [_sanitize_responsible_ai(c) for c in raw_exp.concerns if c]
    if not cleaned_concerns:
        cleaned_concerns.append("Validate remote operating rhythm and team communication cadence during onboarding.")
    cleaned_concerns = cleaned_concerns[:3]

    # Sanitize verdict
    cleaned_verdict = _sanitize_responsible_ai(raw_exp.recommendation_verdict)
    if not cleaned_verdict:
        cleaned_verdict = (
            f"Candidate presents a {state['overall_score']:.1f}% compatibility score with strong operational potential."
        )

    # De-duplicate missing requirements
    cleaned_missing = list(dict.fromkeys([_sanitize_responsible_ai(m) for m in audited_missing if m]))

    # Final client consumption payload
    manager_id = manager.get("id") or str(manager.get("manager_id", ""))
    final_payload = {
        "manager_id": manager_id,
        "overall_score": float(state["overall_score"]),
        "factor_scores": state["factor_scores"],
        "strengths": cleaned_strengths,
        "concerns": cleaned_concerns,
        "missing_requirements": cleaned_missing,
        "verdict": cleaned_verdict,
    }

    return {"final_explanation": final_payload}


# 7. Graph Compilation
builder = StateGraph(EvaluationState)
builder.add_node("generate_explanation", generate_explanation_node)
builder.add_node("audit_and_format", audit_and_format_node)

builder.add_edge(START, "generate_explanation")
builder.add_edge("generate_explanation", "audit_and_format")
builder.add_edge("audit_and_format", END)

explainability_graph = builder.compile()


# 8. Exported Runner Function
async def run_explainability_pipeline(
    business: dict,
    manager: dict,
    factor_scores: dict,
    overall_score: float
) -> dict:
    """
    Execute the stateful LangGraph explainability workflow.
    Guarantees score isolation (read-only input), anti-hallucination checks,
    responsible AI sanitization, and fallback resilience.
    """
    initial_state: EvaluationState = {
        "business_profile": business,
        "manager_profile": manager,
        "factor_scores": factor_scores,
        "overall_score": float(overall_score),
        "raw_explanation": None,
        "final_explanation": None,
    }

    try:
        output = await explainability_graph.ainvoke(initial_state)
        final_exp = output.get("final_explanation")
        if final_exp and isinstance(final_exp, dict):
            return final_exp
    except Exception:
        pass

    # Safety net fallback if graph execution itself encounters an unforeseen issue
    fallback_explanation = _generate_fallback_explanation(business, manager, factor_scores, overall_score)
    mgr_id = manager.get("id") or str(manager.get("manager_id", ""))
    return {
        "manager_id": mgr_id,
        "overall_score": float(overall_score),
        "factor_scores": factor_scores,
        "strengths": fallback_explanation.strengths,
        "concerns": fallback_explanation.concerns,
        "missing_requirements": fallback_explanation.missing_requirements,
        "verdict": fallback_explanation.recommendation_verdict,
    }
