"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  ArrowRight,
  ArrowLeft,
  Sparkles,
  CheckCircle2,
  Layers,
  Target,
  Award,
  AlertCircle,
  Loader2,
} from "lucide-react";

import DemoPresetButton, {
  DemoPresetData,
} from "@/components/wizard/DemoPresetButton";
import StepBusinessProfile from "@/components/wizard/StepBusinessProfile";
import StepGoalsAndChallenges from "@/components/wizard/StepGoalsAndChallenges";
import StepRequirementsAndBudget from "@/components/wizard/StepRequirementsAndBudget";
import { WizardFormData, WizardStepKey } from "@/components/wizard/types";
import { getFashionCartDemoData } from "@/lib/api";

const INITIAL_FORM_DATA: WizardFormData = {
  name: "",
  industry: "",
  size: "Small",
  stage: "Growth",
  location: "",
  employee_count: 0,
  business_model: "Online Retail",
  goals: "",
  challenges: "",
  required_skills: [],
  salary_budget: 2000,
  work_arrangement: "Hybrid",
};

const STEP_DEFINITIONS = [
  {
    step: 1 as WizardStepKey,
    title: "Business Profile",
    subtitle: "Firmographics & Stage",
    icon: Layers,
  },
  {
    step: 2 as WizardStepKey,
    title: "Goals & Bottlenecks",
    subtitle: "Real Operational Needs",
    icon: Target,
  },
  {
    step: 3 as WizardStepKey,
    title: "Requirements & Budget",
    subtitle: "Skills & Compensation",
    icon: Award,
  },
];

function MatchWizardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const isDemo = searchParams.get("demo") === "true";

  const [currentStep, setCurrentStep] = useState<WizardStepKey>(1);
  const [formData, setFormData] = useState<WizardFormData>(INITIAL_FORM_DATA);
  const [isPresetLoaded, setIsPresetLoaded] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Auto-hydrate if ?demo=true in URL query parameters via live API call
  useEffect(() => {
    if (isDemo && !isPresetLoaded) {
      getFashionCartDemoData()
        .then((data) => {
          handleLoadPreset({
            name: data.name,
            industry: data.industry,
            size: data.size || "Small",
            stage: data.stage || "Growth",
            location: data.location || "Lahore, Pakistan",
            employee_count: data.employee_count || 12,
            business_model: data.business_model || "Online Retail",
            goals: data.goals || "",
            challenges: data.challenges || data.core_problem || "",
            required_skills: data.required_skills || [],
            salary_budget: data.salary_budget || data.monthly_budget_usd || 2000,
            work_arrangement: data.work_arrangement || "Hybrid",
          });
        })
        .catch((err) => {
          console.error("Failed to auto-fetch demo preset from API:", err);
        });
    }
  }, [isDemo, isPresetLoaded]);

  // Load preset handler
  const handleLoadPreset = (preset: DemoPresetData) => {
    setFormData((prev) => ({
      ...prev,
      ...preset,
    }));
    setIsPresetLoaded(true);
    setErrors({});
  };

  const updateFormData = (updates: Partial<WizardFormData>) => {
    setFormData((prev) => ({
      ...prev,
      ...updates,
    }));
    const updatedKeys = Object.keys(updates);
    setErrors((prev) => {
      const next = { ...prev };
      updatedKeys.forEach((key) => delete next[key]);
      return next;
    });
  };

  // Step-specific field validation
  const validateCurrentStep = (step: WizardStepKey): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.name.trim()) {
        newErrors.name = "Company name is required.";
      }
      if (!formData.industry.trim()) {
        newErrors.industry = "Industry domain is required.";
      }
      if (!formData.employee_count || formData.employee_count <= 0) {
        newErrors.employee_count = "Please provide an employee count greater than 0.";
      }
      if (!formData.stage) {
        newErrors.stage = "Please select a growth stage.";
      }
    } else if (step === 2) {
      if (!formData.goals.trim()) {
        newErrors.goals = "Please outline your primary goals for the next 6-12 months.";
      }
      if (!formData.challenges.trim()) {
        newErrors.challenges = "Please describe your operational bottlenecks or problems.";
      }
    } else if (step === 3) {
      if (!formData.salary_budget || formData.salary_budget <= 0) {
        newErrors.salary_budget = "Monthly salary budget ceiling must be greater than $0.";
      }
      if (!formData.required_skills || formData.required_skills.length === 0) {
        newErrors.required_skills = "Please select or enter at least one required skill.";
      }
      if (!formData.work_arrangement) {
        newErrors.work_arrangement = "Please specify a preferred work arrangement.";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateCurrentStep(currentStep)) {
      if (currentStep < 3) {
        setCurrentStep((prev) => (prev + 1) as WizardStepKey);
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as WizardStepKey);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateCurrentStep(3)) {
      return;
    }

    setIsSubmitting(true);

    try {
      const businessPayload = {
        name: formData.name,
        industry: formData.industry,
        size: formData.size,
        stage: formData.stage,
        location: formData.location || "Lahore, Pakistan",
        employee_count: formData.employee_count,
        business_model: formData.business_model,
        goals: formData.goals,
        challenges: formData.challenges,
        required_skills: formData.required_skills,
        salary_budget: formData.salary_budget,
        monthly_budget_usd: formData.salary_budget,
        work_arrangement: formData.work_arrangement,
        is_demo: isPresetLoaded || formData.name.toLowerCase() === "fashioncart",
      };

      if (typeof window !== "undefined") {
        sessionStorage.setItem("bizmatch_business_data", JSON.stringify(businessPayload));
        sessionStorage.setItem("bizmatch_business_payload", JSON.stringify(businessPayload));
      }

      router.push("/match/analyzing");
    } catch (err) {
      console.error("Error storing session data:", err);
      setIsSubmitting(false);
    }
  };

  const handleInstantAnalyze = async () => {
    setIsSubmitting(true);
    try {
      let dataToSave = formData;
      if (!isPresetLoaded || !formData.name) {
        const livePreset = await getFashionCartDemoData();
        dataToSave = {
          name: livePreset.name,
          industry: livePreset.industry,
          size: livePreset.size || "Small",
          stage: livePreset.stage || "Growth",
          location: livePreset.location || "Lahore, Pakistan",
          employee_count: livePreset.employee_count || 12,
          business_model: livePreset.business_model || "Online Retail",
          goals: livePreset.goals || "",
          challenges: livePreset.challenges || livePreset.core_problem || "",
          required_skills: livePreset.required_skills || [],
          salary_budget: livePreset.salary_budget || livePreset.monthly_budget_usd || 2000,
          work_arrangement: livePreset.work_arrangement || "Hybrid",
        };
      }

      const businessPayload = {
        name: dataToSave.name,
        industry: dataToSave.industry,
        size: dataToSave.size,
        stage: dataToSave.stage,
        location: dataToSave.location,
        employee_count: dataToSave.employee_count,
        business_model: dataToSave.business_model,
        goals: dataToSave.goals,
        challenges: dataToSave.challenges,
        required_skills: dataToSave.required_skills,
        salary_budget: dataToSave.salary_budget,
        monthly_budget_usd: dataToSave.salary_budget,
        work_arrangement: dataToSave.work_arrangement,
        is_demo: true,
      };

      if (typeof window !== "undefined") {
        sessionStorage.setItem("bizmatch_business_data", JSON.stringify(businessPayload));
        sessionStorage.setItem("bizmatch_business_payload", JSON.stringify(businessPayload));
      }
      router.push("/match/analyzing");
    } catch (err) {
      console.error("Instant analyze error:", err);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[85vh] py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
      {/* Top Demo Fast-Track Hydration Banner */}
      <DemoPresetButton
        onLoadPreset={handleLoadPreset}
        onInstantAnalyze={handleInstantAnalyze}
        isLoaded={isPresetLoaded}
      />

      {/* Step Indicator Header */}
      <div className="mb-6">
        {/* Mobile Compact Step Indicator */}
        <div className="sm:hidden mb-4 p-3 rounded-lg bg-white border border-slate-200 shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold">
              {currentStep}
            </span>
            <span className="text-xs font-bold text-slate-800">
              Step {currentStep} of 3 · {STEP_DEFINITIONS[currentStep - 1].title}
            </span>
          </div>
          <span className="text-xs font-semibold text-indigo-600">
            {Math.round((currentStep / 3) * 100)}%
          </span>
        </div>

        {/* Desktop Step Header */}
        <div className="hidden sm:flex items-center justify-between mb-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-200 mb-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Needs Assessment Wizard</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              Define Your Business &amp; Operational Needs
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 mt-0.5">
              Step {currentStep} of 3: {STEP_DEFINITIONS[currentStep - 1].title}
            </p>
          </div>

          <div className="text-right text-xs text-slate-500 font-medium">
            Assessment Progress: <strong className="text-indigo-600 font-bold">{Math.round((currentStep / 3) * 100)}%</strong>
          </div>
        </div>

        {/* Desktop Connected Stepper */}
        <div className="hidden sm:grid grid-cols-3 gap-3 border-b border-slate-200 pb-5">
          {STEP_DEFINITIONS.map((def) => {
            const Icon = def.icon;
            const isCompleted = currentStep > def.step;
            const isCurrent = currentStep === def.step;

            return (
              <button
                key={def.step}
                type="button"
                onClick={() => {
                  if (def.step < currentStep || validateCurrentStep(currentStep)) {
                    setCurrentStep(def.step);
                  }
                }}
                className={`flex items-center gap-3 p-3 rounded-lg border text-left transition-all ${
                  isCurrent
                    ? "bg-white border-indigo-600 shadow-sm ring-1 ring-indigo-600"
                    : isCompleted
                    ? "bg-slate-50 border-slate-200 text-slate-800 hover:bg-white"
                    : "bg-slate-50/50 border-slate-200 text-slate-400 cursor-not-allowed"
                }`}
              >
                <div
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md font-bold text-xs ${
                    isCompleted
                      ? "bg-emerald-100 text-emerald-700"
                      : isCurrent
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-200 text-slate-500"
                  }`}
                >
                  {isCompleted ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Icon className="w-3.5 h-3.5" />}
                </div>
                <div className="min-w-0">
                  <p
                    className={`text-xs font-bold truncate ${
                      isCurrent ? "text-slate-900" : isCompleted ? "text-slate-800" : "text-slate-500"
                    }`}
                  >
                    {def.title}
                  </p>
                  <p className="text-[11px] text-slate-500 truncate">{def.subtitle}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Wizard Form Card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-sm">
        <form onSubmit={currentStep === 3 ? handleSubmit : (e) => { e.preventDefault(); handleNext(); }}>
          {/* Step 1 Component */}
          {currentStep === 1 && (
            <StepBusinessProfile
              data={formData}
              onChange={updateFormData}
              errors={errors}
            />
          )}

          {/* Step 2 Component */}
          {currentStep === 2 && (
            <StepGoalsAndChallenges
              data={formData}
              onChange={updateFormData}
              errors={errors}
            />
          )}

          {/* Step 3 Component */}
          {currentStep === 3 && (
            <StepRequirementsAndBudget
              data={formData}
              onChange={updateFormData}
              errors={errors}
            />
          )}

          {/* Validation Alert Summary if any */}
          {Object.keys(errors).length > 0 && (
            <div className="mt-6 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-center gap-2.5 text-xs text-rose-700">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>Please resolve the highlighted fields before proceeding.</span>
            </div>
          )}

          {/* Navigation Controls Footer */}
          <div className="mt-8 pt-5 border-t border-slate-200 flex items-center justify-between gap-4">
            <div>
              {currentStep > 1 && (
                <button
                  type="button"
                  id="wizard-back-btn"
                  onClick={handleBack}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span>Back</span>
                </button>
              )}
            </div>

            <div className="flex items-center gap-3">
              {currentStep < 3 ? (
                <button
                  type="button"
                  id="wizard-next-btn"
                  onClick={handleNext}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 text-xs font-bold transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                >
                  <span>
                    {currentStep === 1
                      ? "Next: Goals & Bottlenecks"
                      : "Next: Requirements & Budget"}
                  </span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              ) : (
                <button
                  type="submit"
                  id="wizard-submit-btn"
                  disabled={isSubmitting}
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 text-xs font-bold transition-all shadow-sm disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Saving Requirements...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Analyze &amp; Calculate Deterministic Matches</span>
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export const dynamic = "force-dynamic";

export default function MatchWizardPage() {

  return (
    <Suspense
      fallback={
        <div className="flex min-h-[60vh] items-center justify-center text-slate-600">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
        </div>
      }
    >
      <MatchWizardContent />
    </Suspense>
  );
}
