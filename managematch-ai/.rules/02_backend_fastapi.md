# Backend API & Database Rules

## Tech Stack
- Framework: Python 3.11+ / FastAPI
- ORM/Database: SQLAlchemy or SQLModel / PostgreSQL
- Data Validation: Pydantic V2

## Core Data Models
- Business:
  - id, name, industry, size, stage, goals, challenges, required_skills, required_experience, leadership_requirements, budget, work_arrangement.
- Manager:
  - id, name, title, skills, years_experience, industries, previous_roles, management_experience, leadership_score, achievements, salary_expectation, availability, work_preference.
- MatchRecord:
  - id, business_id, manager_id, overall_score, industry_score, skills_score, experience_score, leadership_score, stage_score, salary_score, strengths, weaknesses, risks, explanation.

## REST Endpoints
- POST /api/analyze-requirements: Accepts business goals & problems text, returns extracted structured requirements.
- POST /api/matches/calculate: Runs deterministic scoring against the manager pool and returns ranked candidates.
- POST /api/matches/explain: Generates qualitative strengths, concerns, and trade-offs for a chosen candidate.
- GET /api/managers: Returns the seeded manager list.
- GET /api/businesses: Returns seeded or saved business profiles.

## Implementation Standards
- Use asynchronous route handlers (`async def`).
- Handle all exceptions gracefully with standard JSON responses: `{"success": bool, "data": ..., "error": ...}`.
- Store the Gemini API key in an environment variable (`GEMINI_API_KEY`) and initialize the client once as a shared service.