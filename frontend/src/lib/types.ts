export interface Business {
  id: string;
  name: string;
  industry: string;
  stage: string;
  monthly_budget_usd: number;
  core_problem: string;
  primary_goals: string[];
  required_skills: string[];
  raw_founder_notes?: string;
}

export interface Manager {
  id: string;
  name: string;
  role_title: string;
  monthly_rate_usd: number;
  verified_stages: string[];
  industries: string[];
  core_skills: string[];
  years_experience: number;
  location: string;
  verified_track_record: string;
  education: string;
  availability: string;
}

export interface MatchRecord {
  id: string;
  business_id: string;
  manager_id: string;
  overall_score: number;
  factor_scores: {
    industry: number;
    skills: number;
    stage: number;
    budget: number;
  };
  qualitative_analysis?: {
    strengths: string[];
    concerns: string[];
    missing_requirements: string[];
    verdict: string;
  };
}
