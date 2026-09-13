"use client";

import React from "react";
import { CheckCircle2, Loader2, Sparkles, Cpu, Award } from "lucide-react";

export type PipelineStepId = 1 | 2 | 3;

interface PipelineProgressProps {
  currentStep: PipelineStepId;
  completedSteps: PipelineStepId[];
}

interface StepConfig {
  id: PipelineStepId;
  title: string;
  subcaption: string;
  icon: React.ElementType;
  badge: string;
}

const STEPS: StepConfig[] = [
  {
    id: 1,
    title: "Analyzing business goals & operational bottlenecks...",
    subcaption:
      "Extracting structured priorities and key management competencies via Gemini AI...",
    icon: Sparkles,
    badge: "AI Extraction",
  },
  {
    id: 2,
    title: "Evaluating candidate pool against 6 fit factors...",
    subcaption:
      "Calculating Industry, Skills, Experience, Scale, Stage, and Salary alignment...",
    icon: Cpu,
    badge: "Deterministic Matcher",
  },
  {
    id: 3,
    title: "Synthesizing executive explainability insights...",
    subcaption:
      "Compiling strengths, risk trade-offs, and final decision scorecards...",
    icon: Award,
    badge: "Explainability Synthesis",
  },
];

export default function PipelineProgress({
  currentStep,
  completedSteps,
}: PipelineProgressProps) {
  // Calculate percentage: 1: 33%, 2: 66%, 3: 100% (if completed)
  const progressPercent =
    completedSteps.length === 3
      ? 100
      : completedSteps.length === 2
      ? 75
      : completedSteps.length === 1
      ? 45
      : 20;

  return (
    <div className="w-full space-y-4">
      <div className="space-y-3">
        {STEPS.map((step) => {
          const isCompleted = completedSteps.includes(step.id);
          const isActive = currentStep === step.id && !isCompleted;

          return (
            <div
              key={step.id}
              className={`relative overflow-hidden rounded-xl border p-4 sm:p-5 transition-all duration-300 ${
                isActive
                  ? "bg-indigo-50/70 border-indigo-500 shadow-sm ring-1 ring-indigo-500/30"
                  : isCompleted
                  ? "bg-white border-emerald-200 text-slate-800"
                  : "bg-slate-50/60 border-slate-200 opacity-60 text-slate-400"
              }`}
            >
              <div className="flex items-start gap-3.5">
                {/* Status Indicator Icon */}
                <div className="shrink-0 mt-0.5">
                  {isCompleted ? (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-sm font-bold animate-in zoom-in-75 duration-200">
                      <CheckCircle2 className="h-4 w-4" />
                    </div>
                  ) : isActive ? (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm ring-2 ring-indigo-200">
                      <Loader2 className="h-4 w-4 animate-spin text-white" />
                    </div>
                  ) : (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-300 bg-white text-slate-400 font-mono text-xs">
                      {step.id}
                    </div>
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-grow min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                        isActive
                          ? "bg-indigo-100 text-indigo-800 border-indigo-200"
                          : isCompleted
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : "bg-slate-100 text-slate-500 border-slate-200"
                      }`}
                    >
                      {step.badge}
                    </span>
                  </div>

                  <p
                    className={`text-xs sm:text-sm font-bold leading-snug ${
                      isActive
                        ? "text-indigo-950"
                        : isCompleted
                        ? "text-slate-900"
                        : "text-slate-400"
                    }`}
                  >
                    {step.title}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                    {step.subcaption}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Subtle Real-time Progress Bar Across Bottom */}
      <div className="pt-2">
        <div className="flex items-center justify-between text-xs text-slate-500 font-medium mb-1.5 px-0.5">
          <span>Overall Analysis Completion</span>
          <span className="font-bold text-indigo-600 font-mono">{progressPercent}%</span>
        </div>
        <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-600 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>
    </div>
  );
}
