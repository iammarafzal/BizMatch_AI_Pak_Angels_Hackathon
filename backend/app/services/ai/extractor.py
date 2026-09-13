import os
import re
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.core.ai_client import gemini_manager
from app.schemas.match import StructuredRequirements, AnalyzeRequirementsRequest

# Extraction Prompt
extraction_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert executive talent architect for high-growth startups and enterprises. "
        "Your objective is to analyze unstructured founder text, business context, goals, and operational challenges, "
        "and translate them into structured, actionable hiring requirements without calculating numerical scores.\n\n"
        "Guidelines:\n"
        "1. Identify the core industry or vertical (e.g., 'E-Commerce', 'B2B SaaS', 'Logistics', 'FinTech', 'HealthTech').\n"
        "2. Infer the business stage (e.g., 'Early/Idea', 'Seed', 'Growth', 'Scale', 'Enterprise').\n"
        "3. Extract 3-4 concrete strategic or operational priorities.\n"
        "4. Standardize technical, managerial, and operational skills (e.g., 'Operations Management', 'Process Optimization', 'Team Leadership', 'Supply Chain').\n"
        "5. Formulate domain and leadership experience profiles required to execute on the business goals.\n"
        "6. Return strictly valid structured output matching the schema."
    ),
    (
        "human",
        "Business Name: {business_name}\n"
        "Stated Industry: {industry}\n"
        "Stated Stage: {stage}\n"
        "Founder Goals:\n{goals}\n\n"
        "Operational Challenges & Bottlenecks:\n{challenges}\n\n"
        "Additional Notes & Preferences:\n{raw_notes}"
    )
])

def _fallback_heuristic_extraction(payload: AnalyzeRequirementsRequest) -> StructuredRequirements:
    """
    Resilient fallback extraction if LLM API is unavailable, unconfigured, or hits quota.
    Analyzes text semantics and extracts structured hiring criteria for demo stability.
    """
    text = (
        (payload.goals or "") + " " +
        (payload.challenges or "") + " " +
        (payload.raw_preferences or "") + " " +
        (payload.industry or "")
    ).lower()

    # 1. Infer Industry
    if any(w in text for w in ["e-commerce", "ecommerce", "retail", "orders", "fulfillment", "store", "shop"]):
        industry = "E-Commerce"
    elif any(w in text for w in ["saas", "software", "api", "sprint", "developers", "code", "cloud"]):
        industry = "B2B SaaS"
    elif any(w in text for w in ["logistics", "fleet", "freight", "truck", "dispatch", "warehouse", "delivery"]):
        industry = "Logistics"
    elif any(w in text for w in ["fintech", "payment", "fraud", "kyc", "aml", "banking"]):
        industry = "FinTech"
    elif any(w in text for w in ["health", "clinic", "medical", "patient", "clinical", "telehealth"]):
        industry = "HealthTech"
    else:
        industry = payload.industry or "Technology & Commerce"

    # 2. Infer Stage
    if any(w in text for w in ["double", "scale", "scaling", "expand", "growth", "increased significantly"]):
        stage = "Growth"
    elif any(w in text for w in ["mvp", "prototype", "launch", "validate", "seed", "0 to 1"]):
        stage = "Seed"
    else:
        stage = payload.stage or "Growth"

    # 3. Extract Skills & Priorities based on text signals
    skills = []
    priorities = []
    experiences = []

    # Operations & Process Optimization
    if any(w in text for w in ["fulfillment", "disorganized", "process", "chaos", "bottleneck", "orders"]):
        skills.extend(["Operations Management", "Process Optimization"])
        priorities.append("Reorganize order fulfillment workflows and eliminate delivery bottlenecks")
        experiences.append("Hands-on fulfillment and operations process design")

    # Team Leadership & Role Clarification
    if any(w in text for w in ["employees", "roles", "responsibilities", "team", "accountability", "hire", "leader"]):
        skills.append("Team Management")
        priorities.append("Establish clearly defined employee responsibilities and standard operating procedures (SOPs)")
        experiences.append("Cross-functional team leadership and operational accountability")

    # Supply Chain
    if any(w in text for w in ["supply", "chain", "warehouse", "dispatch", "inventory", "stock"]):
        skills.append("Supply Chain")
        priorities.append("Implement standard inventory handling and dispatch procedures")
        experiences.append("Warehouse inventory management and vendor coordination")

    # Product / Tech
    if any(w in text for w in ["sprint", "roadmap", "feature", "product", "agile", "churn"]):
        skills.extend(["Technical Product Management", "Agile / Scrum"])
        priorities.append("Implement structured agile sprint cadences and product roadmaps")
        experiences.append("B2B SaaS product strategy and technical roadmap governance")

    # Scaling
    if any(w in text for w in ["double revenue", "expand", "scale", "market", "growth"]):
        skills.append("Growth Strategy")
        priorities.append("Scale operational capacity to support 2x revenue growth")
        experiences.append("Scaling operations during high-velocity growth phases")

    # Ensure minimum standard items
    if not skills:
        skills = ["Operations Management", "Process Optimization", "Team Management"]
    if not priorities:
        priorities = ["Streamline core operations", "Define team roles", "Support revenue expansion"]
    if not experiences:
        experiences = ["Operational leadership", "Standard operating procedures (SOPs) development"]

    # De-duplicate while preserving order
    unique_skills = list(dict.fromkeys(skills))
    unique_priorities = list(dict.fromkeys(priorities))[:4]
    unique_experiences = list(dict.fromkeys(experiences))

    return StructuredRequirements(
        industry=industry,
        business_stage=stage,
        key_priorities=unique_priorities,
        required_skills=unique_skills,
        experience_requirements=unique_experiences,
        experience_profile=unique_experiences
    )

async def extract_requirements(payload: AnalyzeRequirementsRequest) -> StructuredRequirements:
    """
    Extract structured hiring requirements from natural language founder input
    using Google Gemini via dual-key failover manager, with fallback heuristic resilience.
    """
    inputs = {
        "business_name": payload.name or "Startup",
        "industry": payload.industry or "Unspecified",
        "stage": payload.stage or "Unspecified",
        "goals": payload.goals or "Not specified",
        "challenges": payload.challenges or "Not specified",
        "raw_notes": payload.raw_preferences or "None"
    }

    def chain_builder(llm_instance: ChatGoogleGenerativeAI):
        return extraction_prompt | llm_instance.with_structured_output(StructuredRequirements)

    def fallback_handler(inps: dict) -> StructuredRequirements:
        return _fallback_heuristic_extraction(payload)

    return await gemini_manager.execute_with_failover(
        chain_builder=chain_builder,
        inputs=inputs,
        fallback_fn=fallback_handler
    )
