# System Architecture & Global Constraints

## Project Overview
ManageMatch AI is an explainable decision-support system that analyzes a business's context (stage, goals, problems, budget) and matches it with curated manager profiles.
- Stack: Next.js (Frontend), FastAPI (Backend), PostgreSQL (Database), Gemini (LLM).
- Scope: Hackathon MVP with 5–10 sample businesses and 10–20 seed manager profiles.

## Non-Negotiable Constraints
- No complex authentication, payment flows, messaging, or live resume uploaders.
- Do not use LangChain, LangGraph, or custom vector databases/RAG systems.
- LLMs must NEVER calculate numerical match scores. All numerical scores (0–100) are generated deterministically by the scoring engine.
- LLM tasks are strictly limited to:
  1. Parsing unstructured founder text into structured requirements.
  2. Generating qualitative explanations (strengths, gaps, risks, synthesis).
- The frontend must never call AI provider SDKs directly. All requests pass through the backend API.
- Never hallucinate candidate background. If a skill or experience detail is not present in the manager profile, mark it as "Not specified".