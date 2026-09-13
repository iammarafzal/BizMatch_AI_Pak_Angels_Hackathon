export interface WizardFormData {
  name: string;
  industry: string;
  size: string;
  stage: string;
  location: string;
  employee_count: number;
  business_model: string;
  goals: string;
  challenges: string;
  required_skills: string[];
  salary_budget: number;
  work_arrangement: string;
}

export type WizardStepKey = 1 | 2 | 3;
