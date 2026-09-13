from fastapi import APIRouter, HTTPException, status
from app.schemas.match import AnalyzeRequirementsRequest, StructuredRequirements
from app.services.ai.extractor import extract_requirements

router = APIRouter(tags=["Requirements Extraction"])

@router.post("/analyze-requirements", response_model=StructuredRequirements)
async def analyze_requirements(payload: AnalyzeRequirementsRequest):
    """
    Extract structured hiring requirements, priorities, and skills from founder goals and challenges.
    Uses Google Gemini via LangChain with automatic fallback.
    """
    try:
        requirements: StructuredRequirements = await extract_requirements(payload)
        return requirements
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Requirement extraction encountered an error: {str(exc)}"
        )
