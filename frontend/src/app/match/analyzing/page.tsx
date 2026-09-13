"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  AlertTriangle,
  RotateCcw,
  ArrowRight,
  ShieldCheck,
  Building2,
} from "lucide-react";
import PipelineProgress, {
  PipelineStepId,
} from "@/components/processing/PipelineProgress";
import { analyzeRequirements, calculateMatches } from "@/lib/api";
import { Business, BatchMatchResponse } from "@/lib/types";

export const dynamic = "force-dynamic";

export default function AnalyzingPage() {

  const router = useRouter();

  const [currentStep, setCurrentStep] = useState<PipelineStepId>(1);
  const [completedSteps, setCompletedSteps] = useState<PipelineStepId[]>([]);
  const [businessData, setBusinessData] = useState<Partial<Business> | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [errorState, setErrorState] = useState<{
    hasError: boolean;
    message: string;
  }>({ hasError: false, message: "" });
  const [isRetrying, setIsRetrying] = useState(false);

  const executionLock = useRef(false);

  const runPipeline = useCallback(
    async (payload: Record<string, unknown>) => {
      setErrorState({ hasError: false, message: "" });
      setCurrentStep(1);
      setCompletedSteps([]);

      let resolvedBizId = (payload.id as string) || "biz-fashioncart";
      if (
        payload.is_demo ||
        !payload.id ||
        payload.id === "biz_01" ||
        (payload.name &&
          String(payload.name).toLowerCase().includes("fashioncart"))
      ) {
        resolvedBizId = "biz-fashioncart";
      }

      try {
        // --- STEP 1: Requirement Extraction (AI) ---
        setCurrentStep(1);
        const startTimeStep1 = Date.now();
        let extractedRequirements: Record<string, unknown> | null = null;

        try {
          if (payload.goals || payload.challenges) {
            const aiRes = await analyzeRequirements({
              name: String(payload.name || "FashionCart"),
              industry: String(payload.industry || "Fashion E-commerce"),
              stage: String(payload.stage || "Growth"),
              goals: String(payload.goals || ""),
              challenges: String(payload.challenges || ""),
              raw_preferences: String(payload.raw_preferences || payload.challenges || ""),
            });

            if (aiRes) {
              extractedRequirements = aiRes as unknown as Record<string, unknown>;
              sessionStorage.setItem(
                "bizmatch_analyzed_requirements",
                JSON.stringify(aiRes)
              );
            }
          }
        } catch (err) {
          console.warn("AI requirement extraction note:", err);
        }

        const elapsed1 = Date.now() - startTimeStep1;
        if (elapsed1 < 650) {
          await new Promise((res) => setTimeout(res, 650 - elapsed1));
        }

        setCompletedSteps((prev) => [...prev, 1]);

        // --- STEP 2: Deterministic Factor Scoring (Deterministic Engine) ---
        setCurrentStep(2);
        const startTimeStep2 = Date.now();

        let matchResult: BatchMatchResponse | null = null;
        try {
          // Feed real form data merged with dynamic extracted requirements into calculateMatches
          const isDemoScenario = Boolean(
            payload.is_demo ||
            (payload.name && String(payload.name).toLowerCase().includes("fashioncart"))
          );

          if (isDemoScenario) {
            matchResult = await calculateMatches(resolvedBizId);
          } else {
            const dynamicSkills = Array.isArray(extractedRequirements?.required_skills) && (extractedRequirements?.required_skills as string[]).length > 0
              ? (extractedRequirements?.required_skills as string[])
              : ((payload.required_skills as string[]) || []);

            const dynamicExp = Array.isArray(extractedRequirements?.experience_requirements)
              ? (extractedRequirements?.experience_requirements as string[])
              : [];

            const customBiz = {
              name: String(payload.name || "Custom Business"),
              industry: String(extractedRequirements?.industry || payload.industry || "Technology & Commerce"),
              stage: String(extractedRequirements?.business_stage || payload.stage || "Growth"),
              salary_budget: Number(payload.salary_budget || 2000),
              monthly_budget_usd: Number(payload.salary_budget || 2000),
              location: String(payload.location || "Lahore, Pakistan"),
              employee_count: Number(payload.employee_count || 12),
              business_model: String(payload.business_model || "Online Retail"),
              goals: String(payload.goals || ""),
              challenges: String(payload.challenges || ""),
              required_skills: dynamicSkills,
              required_experience: dynamicExp,
              work_arrangement: String(payload.work_arrangement || "Hybrid"),
            };

            matchResult = await calculateMatches({ business_data: customBiz });

            // Persist the enriched business profile for results dashboard
            if (matchResult?.business_id) {
              resolvedBizId = matchResult.business_id;
              sessionStorage.setItem("bizmatch_business_data", JSON.stringify({
                ...customBiz,
                id: matchResult.business_id,
              }));
            }
          }

          if (matchResult && matchResult.matches && matchResult.matches.length > 0) {
            if (matchResult.business_id) {
              resolvedBizId = matchResult.business_id;
            }
            sessionStorage.setItem(
              "bizmatch_calculated_matches",
              JSON.stringify(matchResult.matches)
            );
            sessionStorage.setItem("bizmatch_selected_biz_id", resolvedBizId);
          } else {
            throw new Error("Match engine returned zero eligible candidates.");
          }
        } catch (err: unknown) {
          console.error("Backend calculate matches error:", err);
          const msg = err instanceof Error ? err.message : "Calculation failed.";
          setErrorState({
            hasError: true,
            message: `FastAPI Match Engine Error: ${msg}. Please ensure backend server is accessible.`,
          });
          return;
        }

        const elapsed2 = Date.now() - startTimeStep2;
        if (elapsed2 < 700) {
          await new Promise((res) => setTimeout(res, 700 - elapsed2));
        }

        setCompletedSteps((prev) => [...prev, 2]);

        // --- STEP 3: Explainability Synthesis ---
        setCurrentStep(3);
        await new Promise((res) => setTimeout(res, 700));
        setCompletedSteps((prev) => [...prev, 3]);

        // Smooth transition to results page
        setIsRedirecting(true);
        setTimeout(() => {
          router.push("/match/results");
        }, 500);
      } catch (err: unknown) {
        console.error("Pipeline failure:", err);
        const msg = err instanceof Error ? err.message : "Unexpected pipeline error.";
        setErrorState({
          hasError: true,
          message: msg,
        });
      }
    },
    [router]
  );

  useEffect(() => {
    if (typeof window === "undefined") return;

    if (executionLock.current) return;
    executionLock.current = true;

    const storedData = sessionStorage.getItem("bizmatch_business_data");
    if (!storedData) {
      router.replace("/match");
      return;
    }

    try {
      const parsed = JSON.parse(storedData) as Partial<Business>;
      setBusinessData(parsed);
      runPipeline(parsed as Record<string, unknown>);
    } catch {
      router.replace("/match");
    }
  }, [router, runPipeline]);

  const handleRetry = () => {
    setIsRetrying(true);
    setErrorState({ hasError: false, message: "" });
    if (businessData) {
      runPipeline(businessData as Record<string, unknown>).finally(() => {
        setIsRetrying(false);
      });
    } else {
      router.push("/match");
    }
  };

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-xl mx-auto space-y-6">
        {/* Header Eyebrow & Title */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-200">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Deterministic Scoring Engine &amp; AI</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
            Evaluating Candidate Compatibility
          </h1>

          {/* Active Business Chip */}
          {businessData && (
            <div className="inline-flex flex-wrap items-center justify-center gap-2 pt-1 text-xs text-slate-600">
              <span className="flex items-center gap-1 font-semibold text-slate-800 bg-white px-2.5 py-1 rounded-md border border-slate-200 shadow-sm">
                <Building2 className="w-3.5 h-3.5 text-indigo-600" />
                {businessData.name || "Business"}
              </span>
              <span className="bg-white px-2 py-1 rounded-md border border-slate-200 text-slate-600">
                {businessData.industry || "General Industry"}
              </span>
              <span className="bg-white px-2 py-1 rounded-md border border-slate-200 text-slate-600">
                {businessData.stage || "Growth"} Stage
              </span>
              <span className="bg-white px-2 py-1 rounded-md border border-slate-200 text-slate-600 font-mono">
                ${(businessData.salary_budget || 2000).toLocaleString()}/mo
              </span>
            </div>
          )}
        </div>

        {/* Pipeline Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          {errorState.hasError ? (
            <div className="p-5 rounded-xl bg-rose-50 border border-rose-200 space-y-3 text-center">
              <div className="w-10 h-10 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-rose-900">
                  Backend Evaluation Error
                </h3>
                <p className="text-xs text-rose-700 mt-1 max-w-md mx-auto">
                  {errorState.message}
                </p>
              </div>

              <div className="pt-2 flex items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={handleRetry}
                  disabled={isRetrying}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>{isRetrying ? "Retrying..." : "Retry Pipeline"}</span>
                </button>
                <button
                  type="button"
                  onClick={() => router.push("/match")}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50 transition-colors"
                >
                  <span>Edit Wizard Data</span>
                </button>
              </div>
            </div>
          ) : (
            <PipelineProgress
              currentStep={currentStep}
              completedSteps={completedSteps}
            />
          )}

          {isRedirecting && (
            <div className="mt-5 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-center animate-pulse">
              <p className="text-xs font-bold text-emerald-800 flex items-center justify-center gap-1.5">
                <span>Deterministic scoring finalized! Routing to ranked results...</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </p>
            </div>
          )}
        </div>

        {/* Micro Footer Notice */}
        <div className="flex items-center justify-center gap-2 text-xs text-slate-500 text-center">
          <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
          <span>Transparent 6-factor deterministic calculation • Zero hallucination ranking</span>
        </div>
      </div>
    </div>
  );
}
