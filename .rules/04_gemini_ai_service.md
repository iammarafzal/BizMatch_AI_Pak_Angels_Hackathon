# AI Service Architecture: Gemini + LangChain + LangGraph

## 1. Libraries & Setup
- `langchain-google-genai`: Provides `ChatGoogleGenerativeAI` integrated with Gemini.
- `langgraph`: Orchestrates the decision-support evaluation workflow.
- `pydantic`: Enforces strict structured output parsing.

```bash
pip install langchain-core langchain-google-genai langgraph pydantic
```

Initialize model:
```python
import os
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,
    google_api_key=os.environ.get("GEMINI_API_KEY"),
)
```

## 2. Structured Schemas (Pydantic V2)

### Requirement Extraction Schema
```python
from pydantic import BaseModel, Field

class StructuredRequirements(BaseModel):
    industry: str = Field(description="Normalized industry or vertical")
    business_stage: str = Field(description="e.g., Early, Growth, Scaling")
    key_priorities: list[str] = Field(description="Top 3-4 operational priorities")
    required_skills: list[str] = Field(description="Extracted required skills")
    experience_profile: list[str] = Field(description="Contextual experience requirements")
```

### Explainability Schema
```python
from pydantic import BaseModel, Field

class MatchExplanation(BaseModel):
    strengths: list[str] = Field(description="2-4 concrete strengths matching the business context")
    concerns: list[str] = Field(description="Potential friction points or domain gaps")
    missing_requirements: list[str] = Field(description="Required items not evidenced in profile")
    recommendation_verdict: str = Field(description="1-2 sentence decision-support synthesis")
```

## 3. LangChain Pipeline: Requirement Extraction
Convert unstructured founder problem statements into structured business criteria:
```python
from langchain_core.prompts import ChatPromptTemplate

extraction_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert talent architect. Extract structured hiring requirements from founder input."),
    ("human", "Business: {business_name}\nGoals: {goals}\nChallenges: {challenges}\nStated Preferences: {raw_preferences}")
])

extraction_chain = extraction_prompt | llm.with_structured_output(StructuredRequirements)
```

## 4. LangGraph Workflow: Explainable Decision Support
Use LangGraph to coordinate match analysis, verification, and synthesis without letting the model calculate numerical scores:

```text
[Start]
   │
   ▼
[Fetch Candidate & Factor Breakdown]
   │
   ▼
[Generate Match Explanation (Gemini)]
   │
   ▼
[Hallucination & Fairness Audit]
   │
   ▼
[End (Return Formatted Decision Card)]
```

### Graph Implementation
```python
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

class EvaluationState(TypedDict):
    business_profile: Dict[str, Any]
    manager_profile: Dict[str, Any]
    factor_scores: Dict[str, float]
    raw_explanation: MatchExplanation
    final_output: Dict[str, Any]

def generate_explanation_node(state: EvaluationState) -> Dict[str, Any]:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an unbiased executive hiring advisor. Analyze candidate suitability using only provided data."),
        ("human", """
        Business Context: {business_profile}
        Manager Profile: {manager_profile}
        Deterministic Match Scores: {factor_scores}

        Provide strengths, concerns, missing requirements, and a final verdict.
        """)
    ])
    chain = prompt | llm.with_structured_output(MatchExplanation)
    result: MatchExplanation = chain.invoke({
        "business_profile": state["business_profile"],
        "manager_profile": state["manager_profile"],
        "factor_scores": state["factor_scores"],
    })
    return {"raw_explanation": result}

def audit_and_format_node(state: EvaluationState) -> Dict[str, Any]:
    explanation = state["raw_explanation"]
    
    # Verify grounding against manager profile
    manager_skills = set(s.lower() for s in state["manager_profile"].get("skills", []))
    cleaned_strengths = [
        s for s in explanation.strengths
        if not any(banned in s.lower() for banned in ["guaranteed", "predicts"])
    ]
    
    return {
        "final_output": {
            "manager_id": state["manager_profile"]["id"],
            "strengths": cleaned_strengths,
            "concerns": explanation.concerns,
            "missing_requirements": explanation.missing_requirements,
            "verdict": explanation.recommendation_verdict,
            "factor_scores": state["factor_scores"],
        }
    }

builder = StateGraph(EvaluationState)
builder.add_node("generate_explanation", generate_explanation_node)
builder.add_node("audit_and_format", audit_and_format_node)

builder.set_entry_point("generate_explanation")
builder.add_edge("generate_explanation", "audit_and_format")
builder.add_edge("audit_and_format", END)

explainability_graph = builder.compile()
```

## 5. Architectural Guardrails
- **Score Isolation**: Never pass numerical score calculations into LangGraph or LangChain. Scores are injected as read-only inputs from the deterministic Python engine.
- **Anti-Hallucination**: If a requested capability cannot be verified in manager_profile, the agent must list it under missing_requirements or write "Information not provided".
- **Responsible AI**: The prompt must explicitly forbid ranking or evaluating on age, gender, race, marital status, or nationality.