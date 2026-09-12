# Deterministic Matching Engine

## Weighting Model
The engine must compute match compatibility strictly using these deterministic factor weights:
- Industry Relevance: 20%
- Required Skills: 25%
- Relevant Experience: 20%
- Leadership Fit: 15%
- Business Stage Fit: 10%
- Salary Compatibility: 10%

## Calculation Criteria
- Normalize each factor to a 0–100 scale before applying weights.
- Industry & Skills: Compute match overlap against the structured requirements.
- Experience Relevance: Evaluate domain and company stage alignment, not just raw total years of employment.
- Salary Compatibility: Implement soft penalties. If a manager's expected salary exceeds budget by 10%–20%, apply a graduated penalty (e.g., assign 60–75%) rather than assigning 0%.
- Output structure must include the final weighted `overall_score` plus individual factor scores so the frontend can render the transparent breakdown.