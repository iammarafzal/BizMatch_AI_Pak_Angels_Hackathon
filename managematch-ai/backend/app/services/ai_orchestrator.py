import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from app.core.config import settings
from app.schemas.match import QualitativeAnalysis
from app.schemas.business import BusinessCreate

# Initialize Gemini model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,
    google_api_key=settings.GEMINI_API_KEY or "dummy_key",
)

# 1. Requirement Extraction
def extract_business_requirements(goals: str, challenges: str, preferences: str) -> dict:
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert talent architect. Extract structured hiring requirements from founder input. Do not hallucinate budget if not mentioned. If missing, assume zero."),
            ("human", "Goals: {goals}\nChallenges: {challenges}\nStated Preferences: {raw_preferences}")
        ])
        
        chain = prompt | llm.with_structured_output(BusinessCreate)
        result: BusinessCreate = chain.invoke({
            "goals": goals,
            "challenges": challenges,
            "raw_preferences": preferences
        })
        return result.model_dump()
    except Exception as exc:
        # Fallback heuristic if external LLM API is unreachable or unconfigured
        return {
            "name": "Extracted Business Profile",
            "industry": "E-Commerce",
            "stage": "Growth",
            "salary_budget": 2000.0,
            "monthly_budget_usd": 2000.0,
            "goals": goals,
            "primary_goals": [goals] if goals else [],
            "challenges": challenges,
            "core_problem": challenges,
            "required_skills": ["Operations Management", "Process Optimization", "Team Leadership"],
            "raw_founder_notes": preferences
        }

# 2. LangGraph Decision Support Workflow
from typing_extensions import TypedDict

class EvaluationState(TypedDict):
    business_profile: Dict[str, Any]
    manager_profile: Dict[str, Any]
    factor_scores: Dict[str, float]
    raw_explanation: QualitativeAnalysis
    final_output: QualitativeAnalysis

def generate_explanation_node(state: EvaluationState) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an unbiased executive hiring advisor. Analyze candidate suitability using ONLY provided data. Do not guess experience or invent strengths."),
        ("human", """
        Business Context: {business_profile}
        Manager Profile: {manager_profile}
        Deterministic Match Scores: {factor_scores}

        Provide strengths, concerns, missing requirements, and a final verdict. Do not calculate numbers yourself. 
        """)
    ])
    chain = prompt | llm.with_structured_output(QualitativeAnalysis)
    result = chain.invoke({
        "business_profile": state["business_profile"],
        "manager_profile": state["manager_profile"],
        "factor_scores": state["factor_scores"],
    })
    return {"raw_explanation": result}

def audit_and_format_node(state: EvaluationState) -> Dict[str, Any]:
    explanation = state["raw_explanation"]
    
    cleaned_strengths = []
    for s in explanation.strengths:
        if any(banned in s.lower() for banned in ["guaranteed", "predicts"]):
            continue
        cleaned_strengths.append(s)
    
    if not cleaned_strengths:
        cleaned_strengths.append("Information not provided")

    explanation.strengths = cleaned_strengths
    
    return {"final_output": explanation}

builder = StateGraph(EvaluationState)
builder.add_node("generate_explanation", generate_explanation_node)
builder.add_node("audit_and_format", audit_and_format_node)
builder.set_entry_point("generate_explanation")
builder.add_edge("generate_explanation", "audit_and_format")
builder.add_edge("audit_and_format", END)
explainability_graph = builder.compile()

from app.services.ai.explainer_graph import run_explainability_pipeline

async def generate_match_explanation(business: dict, manager: dict, scores: dict) -> QualitativeAnalysis:
    overall = float(scores.get("overall", 85.0) if isinstance(scores, dict) else 85.0)
    res = await run_explainability_pipeline(business, manager, scores, overall)
    return QualitativeAnalysis(
        strengths=res["strengths"],
        concerns=res["concerns"],
        missing_requirements=res.get("missing_requirements", []),
        verdict=res["verdict"],
        manager_id=res.get("manager_id"),
        overall_score=res.get("overall_score"),
        factor_scores=res.get("factor_scores")
    )
