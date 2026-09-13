"use client";

import React from "react";
import {
  CheckCircle2,
  AlertTriangle,
  Info,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

export interface AiExplanationPayload {
  strengths: string[];
  concerns: string[];
  missing_requirements: string[];
  verdict: string;
}

interface AiDecisionCardProps {
  explanation: AiExplanationPayload | null;
  candidateName: string;
  overallScore: number;
  isLoading?: boolean;
}

export default function AiDecisionCard({
  explanation,
  candidateName,
  overallScore,
  isLoading = false,
}: AiDecisionCardProps) {
  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200">
          <div className="h-5 w-48 bg-slate-200 rounded" />
          <div className="h-5 w-16 bg-slate-200 rounded-full" />
        </div>

        {/* 2x2 Skeleton Quadrants */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-36 bg-emerald-50/60 border border-emerald-100 rounded-xl p-4 space-y-2">
            <div className="h-4 w-24 bg-emerald-200 rounded" />
            <div className="h-3 w-full bg-emerald-100 rounded" />
            <div className="h-3 w-4/5 bg-emerald-100 rounded" />
          </div>
          <div className="h-36 bg-amber-50/60 border border-amber-100 rounded-xl p-4 space-y-2">
            <div className="h-4 w-24 bg-amber-200 rounded" />
            <div className="h-3 w-full bg-amber-100 rounded" />
            <div className="h-3 w-4/5 bg-amber-100 rounded" />
          </div>
          <div className="h-32 bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
            <div className="h-4 w-32 bg-slate-200 rounded" />
            <div className="h-3 w-full bg-slate-200 rounded" />
          </div>
          <div className="h-32 bg-indigo-50/60 border border-indigo-100 rounded-xl p-4 space-y-2">
            <div className="h-4 w-28 bg-indigo-200 rounded" />
            <div className="h-3 w-full bg-indigo-100 rounded" />
          </div>
        </div>

        {/* Full-width Verdict Banner Skeleton */}
        <div className="h-28 bg-slate-100 rounded-xl" />
      </div>
    );
  }

  if (!explanation) {
    return (
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-center text-xs text-slate-500">
        AI explainability decision support is currently being calculated for {candidateName}.
      </div>
    );
  }

  const missing = explanation.missing_requirements || [];

  return (
    <div className="space-y-4">
      {/* Header Eyebrow & Title */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Explainable AI Decision Audit
            </h3>
            <p className="text-[11px] text-slate-500">
              Deterministic 6-factor model evaluated against operational profile
            </p>
          </div>
        </div>
        <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-mono font-bold text-emerald-700 border border-emerald-200">
          {Math.round(overallScore)}% Overall Fit
        </span>
      </div>

      {/* 4 Decision Quadrants in a 2x2 Grid on Desktop, Stack on Mobile */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Quadrant 1: Strengths */}
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-4 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-emerald-100 text-emerald-700">
                <CheckCircle2 className="h-4 w-4" />
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800">
                Verified Strengths
              </h4>
            </div>

            <ul className="space-y-1.5">
              {explanation.strengths && explanation.strengths.length > 0 ? (
                explanation.strengths.map((s, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-slate-700 leading-relaxed flex items-start gap-1.5"
                  >
                    <span className="text-emerald-600 font-bold shrink-0 mt-0.5">•</span>
                    <span>{s}</span>
                  </li>
                ))
              ) : (
                <li className="text-xs text-slate-500 italic">
                  No critical strengths flagged.
                </li>
              )}
            </ul>
          </div>
          <span className="text-[10px] text-emerald-700 font-semibold mt-3 block">
            ✓ Deterministic Overlap Confirmed
          </span>
        </div>

        {/* Quadrant 2: Concerns / Trade-offs */}
        <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-4 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-amber-100 text-amber-800">
                <AlertTriangle className="h-4 w-4" />
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-amber-900">
                Identified Trade-offs &amp; Gaps
              </h4>
            </div>

            <ul className="space-y-1.5">
              {explanation.concerns && explanation.concerns.length > 0 ? (
                explanation.concerns.map((c, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-slate-700 leading-relaxed flex items-start gap-1.5"
                  >
                    <span className="text-amber-600 font-bold shrink-0 mt-0.5">•</span>
                    <span>{c}</span>
                  </li>
                ))
              ) : (
                <li className="text-xs text-slate-500 italic">
                  No significant risks detected in current model.
                </li>
              )}
            </ul>
          </div>
          <span className="text-[10px] text-amber-800 font-semibold mt-3 block">
            ⚠ Advisory Risk Mitigation Point
          </span>
        </div>

        {/* Quadrant 3: Missing Requirements */}
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-slate-200 text-slate-700">
                <Info className="h-4 w-4" />
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Missing Requirements
              </h4>
            </div>

            <ul className="space-y-1.5">
              {missing.length > 0 ? (
                missing.map((m, idx) => (
                  <li
                    key={idx}
                    className="text-xs text-slate-600 leading-relaxed flex items-start gap-1.5"
                  >
                    <span className="text-slate-400 font-bold shrink-0 mt-0.5">•</span>
                    <span>{m}</span>
                  </li>
                ))
              ) : (
                <li className="text-xs text-slate-500">
                  All critical firmographic criteria covered.
                </li>
              )}
            </ul>
          </div>
          <span className="text-[10px] text-slate-500 mt-3 block">
            Profile coverage: {missing.length === 0 ? "Complete" : `${missing.length} unfulfilled requirements`}
          </span>
        </div>

        {/* Quadrant 4: Strategic Recommendation Verdict */}
        <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center gap-2 mb-2.5">
              <div className="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-100 text-indigo-700">
                <Sparkles className="h-4 w-4" />
              </div>
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900">
                Recommendation Verdict
              </h4>
            </div>

            <p className="text-xs text-slate-800 leading-relaxed font-medium">
              {explanation.verdict || `Candidate evaluated with ${Math.round(overallScore)}% fit score based on verified factor models.`}
            </p>
          </div>
          <span className="text-[10px] text-indigo-700 font-semibold mt-3 block">
            ✓ Live LangGraph Decision Synthesis
          </span>
        </div>
      </div>

      {/* Strategic Verdict: Full-Width Accent Banner with Indigo Pill Badge */}
      <div className="rounded-xl border border-indigo-200 bg-white p-4 sm:p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-2">
          <span className="px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-[10px] font-bold uppercase tracking-wider border border-indigo-200">
            AI Strategic Verdict
          </span>
          <span className="text-[11px] text-slate-500">Executive Recommendation</span>
        </div>
        <p className="text-sm font-medium text-slate-900 leading-relaxed">
          {explanation.verdict ||
            `Candidate demonstrates strong operational alignment for ${candidateName}'s current stage.`}
        </p>
      </div>

      {/* Human-in-the-loop Advisory Disclaimer */}
      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-center gap-2 text-[11px] text-slate-500">
        <ShieldCheck className="w-4 h-4 text-indigo-600 shrink-0" />
        <span>
          Grounded Gemini explainability based strictly on deterministic factor weights. Final hiring decision rests with the founder.
        </span>
      </div>
    </div>
  );
}
