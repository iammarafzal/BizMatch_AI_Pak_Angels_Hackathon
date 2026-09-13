/**
 * BizMatch AI - Strict Backend API Contracts
 * Aligned 1:1 with FastAPI backend Pydantic models in app/schemas/
 */

export interface Manager {
  id: string;
  name: string;
  title: string;
  role_title?: string | null;
  years_experience?: number | null;
  experience_years?: number | null;
  industries?: string[] | null;
  skills?: string[] | null;
  core_skills?: string[] | null;
  previous_roles?: string[] | null;
  management_experience?: string | null;
  leadership_score?: number | null;
  achievements?: string[] | null;
  salary_expectation?: number | null;
  expected_salary?: number | null;
  monthly_rate_usd?: number | null;
  availability?: string | null;
  location?: string | null;
  work_preference?: string | null;
  work_arrangement?: string | null;
  verified_stages?: string[] | null;
  verified_track_record?: string | null;
  education?: string | null;
  bio?: string | null;
  created_at?: string | null;
}

export interface Business {
  id?: string | null;
  name: string;
  industry: string;
  size?: string | null;
  stage?: string | null;
  location?: string | null;
  employee_count?: number | null;
  business_model?: string | null;
  goals?: string | null;
  challenges?: string | null;
  core_problem?: string | null;
  primary_goals?: string[] | null;
  required_skills?: string[] | null;
  required_experience?: string[] | null;
  leadership_requirements?: string | null;
  salary_budget?: number | null;
  monthly_budget_usd?: number | null;
  work_arrangement?: string | null;
  created_at?: string | null;
}

export type BusinessCreate = Business;

export interface StructuredRequirements {
  industry: string;
  business_stage: string;
  key_priorities: string[];
  required_skills: string[];
  experience_requirements: string[];
  experience_profile?: string[] | null;
}

export interface MatchFactorScores {
  industry_fit: number;
  skills_fit: number;
  experience_fit: number;
  leadership_fit: number;
  stage_fit: number;
  salary_fit: number;
  [key: string]: number | undefined;
}

export interface FactorScores extends MatchFactorScores {
  industry?: number;
  skills?: number;
  stage?: number;
  budget?: number;
  experience?: number;
  leadership?: number;
  salary?: number;
  [key: string]: number | undefined;
}

export interface QualitativeAnalysis {
  strengths: string[];
  concerns: string[];
  missing_requirements: string[];
  verdict: string;
  manager_id?: string | null;
  overall_score?: number | null;
  factor_scores?: Record<string, number> | null;
}

export interface CandidateMatchSummary {
  manager: Manager;
  overall_score: number;
  factor_scores: MatchFactorScores;
  explanation?: QualitativeAnalysis | null;
  qualitative_analysis?: QualitativeAnalysis | null;
}

export interface BatchMatchResponse {
  business_id: string;
  total_evaluated: number;
  matches: CandidateMatchSummary[];
}

export interface CalculateMatchesRequest {
  business_id?: string | null;
  business_data?: BusinessCreate | null;
}

export interface AnalyzeRequirementsRequest {
  name?: string | null;
  industry?: string | null;
  stage?: string | null;
  goals: string;
  challenges: string;
  raw_preferences?: string | null;
}

export interface AnalyzeRequirementsResponse {
  success: boolean;
  data: StructuredRequirements;
}

export interface ExplainMatchRequest {
  business_id: string | number;
  manager_id: string | number;
  custom_business_context?: Record<string, unknown> | null;
}

export interface ExplainMatchResponse {
  success: boolean;
  manager_id: string | number;
  manager_name: string;
  manager_title: string;
  overall_score: number;
  factor_scores: Record<string, number>;
  strengths: string[];
  concerns: string[];
  missing_requirements: string[];
  verdict: string;
  generated_at?: string | null;
  data?: {
    manager_id: string;
    manager_name: string;
    manager_title: string;
    overall_score: number;
    factor_scores: Record<string, number>;
    strengths: string[];
    concerns: string[];
    missing_requirements: string[];
    verdict: string;
    generated_at: string;
  } | null;
}

export interface DemoPresetResponse {
  success: boolean;
  data: Business;
  [key: string]: unknown;
}

export interface ApiErrorResponse {
  success: boolean;
  error: string;
  details?: string[] | Record<string, unknown> | null;
  code?: number;
}
