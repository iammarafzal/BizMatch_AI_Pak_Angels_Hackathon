"use client";

import React, { useEffect, useMemo } from "react";
import {
  X,
  Sparkles,
  Award,
  CheckCircle2,
  AlertTriangle,
  Zap,
} from "lucide-react";
import { MatchRecord } from "@/lib/types";

interface CandidateComparisonTableProps {
  candidates: MatchRecord[];
  budgetCeiling: number;
  onRemoveCandidate: (candidateId: string) => void;
  onViewExplanation: (candidate: MatchRecord) => void;
  onClose: () => void;
}

interface FactorDef {
  key: string;
  aliases: string[];
  label: string;
  weight: string;
  barColor: string;
}

const FACTORS: FactorDef[] = [
  {
    key: "skills_fit",
    aliases: ["skills", "skills_fit"],
    label: "Required Skills Fit",
    weight: "25%",
    barColor: "bg-indigo-600",
  },
  {
    key: "industry_fit",
    aliases: ["industry", "industry_fit"],
    label: "Industry Relevance",
    weight: "20%",
    barColor: "bg-indigo-500",
  },
  {
    key: "experience_fit",
    aliases: ["experience", "experience_fit"],
    label: "Relevant Experience",
    weight: "20%",
    barColor: "bg-teal-600",
  },
  {
    key: "leadership_fit",
    aliases: ["leadership", "leadership_fit"],
    label: "Leadership Fit",
    weight: "15%",
    barColor: "bg-blue-600",
  },
  {
    key: "stage_fit",
    aliases: ["stage", "stage_fit"],
    label: "Business Stage Fit",
    weight: "10%",
    barColor: "bg-violet-600",
  },
  {
    key: "salary_fit",
    aliases: ["salary", "salary_fit"],
    label: "Salary Compatibility",
    weight: "10%",
    barColor: "bg-amber-600",
  },
];

function resolveScore(
  factorMeta: FactorDef,
  scores: Record<string, number | undefined>
): number {
  for (const alias of factorMeta.aliases) {
    if (typeof scores[alias] === "number") {
      return scores[alias]!;
    }
  }
  return 0;
}

export default function CandidateComparisonTable({
  candidates,
  budgetCeiling,
  onRemoveCandidate,
  onViewExplanation,
  onClose,
}: CandidateComparisonTableProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    const origOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = origOverflow;
    };
  }, [onClose]);

  // Identify leaders for trade-off highlights
  const highestMatchCandidate = useMemo(() => {
    if (candidates.length === 0) return null;
    return [...candidates].sort((a, b) => b.overall_score - a.overall_score)[0];
  }, [candidates]);

  const stageFitLeaderId = useMemo(() => {
    if (candidates.length === 0) return null;
    return [...candidates].sort(
      (a, b) => (b.factor_scores.stage_fit ?? 0) - (a.factor_scores.stage_fit ?? 0)
    )[0]?.manager.id;
  }, [candidates]);

  const industryFitLeaderId = useMemo(() => {
    if (candidates.length === 0) return null;
    return [...candidates].sort(
      (a, b) => (b.factor_scores.industry_fit ?? 0) - (a.factor_scores.industry_fit ?? 0)
    )[0]?.manager.id;
  }, [candidates]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-6xl rounded-2xl border border-slate-200 bg-white p-5 sm:p-7 shadow-2xl my-auto max-h-[92vh] flex flex-col focus:outline-none"
        role="dialog"
        aria-modal="true"
      >
        {/* Top Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-200 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
              <Zap className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900 tracking-tight">
                  Candidate Comparison Matrix
                </h3>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600 border border-slate-200">
                  {candidates.length} Profiles Selected
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Parallel trade-off analysis across deterministic factors and compensation models
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            aria-label="Close comparison"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Dynamic Trade-off Callout Banner */}
        <div className="my-3.5 rounded-xl border border-indigo-200 bg-indigo-50/60 p-3 shrink-0">
          <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs">
            <span className="flex items-center gap-1 font-bold text-indigo-900">
              <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
              <span>Key Trade-off Highlights:</span>
            </span>
            {highestMatchCandidate && (
              <span className="inline-flex items-center gap-1 text-emerald-800 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200 font-semibold">
                <Award className="h-3.5 w-3.5 text-emerald-600" />
                <span>
                  Top Overall Fit: <strong>{highestMatchCandidate.manager.name}</strong> ({Math.round(highestMatchCandidate.overall_score)}%)
                </span>
              </span>
            )}
            <span className="text-slate-600 text-xs">
              Budget target: <strong className="text-slate-900 font-mono">${budgetCeiling.toLocaleString()}/mo</strong>
            </span>
          </div>
        </div>

        {/* Comparison Matrix Table (Horizontally Scrollable on mobile, equal columns on desktop) */}
        <div className="overflow-x-auto overflow-y-auto flex-grow border border-slate-200 rounded-xl bg-white">
          <table className="w-full text-left border-collapse min-w-[650px] table-fixed">
            {/* Header Row: Candidate Cards */}
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="p-4 w-48 sm:w-56 sticky left-0 z-20 bg-slate-50 text-xs font-bold text-slate-700 uppercase tracking-wider border-r border-slate-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                  Criteria / Dimension
                </th>
                {candidates.map((cand) => {
                  const mgr = cand.manager;
                  const score = Math.round(cand.overall_score);
                  const isTop = cand.manager.id === highestMatchCandidate?.manager.id;

                  let badgeColor = "bg-slate-100 text-slate-700 border-slate-200";
                  if (score >= 85) {
                    badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
                  } else if (score >= 70) {
                    badgeColor = "bg-amber-50 text-amber-700 border-amber-200";
                  }

                  return (
                    <th
                      key={mgr.id}
                      className="p-4 border-r border-slate-200 align-top relative bg-white"
                    >
                      {/* Remove Candidate Button */}
                      <button
                        type="button"
                        onClick={() => onRemoveCandidate(mgr.id)}
                        className="absolute top-3 right-3 p-1 rounded-md text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
                        title={`Remove ${mgr.name}`}
                      >
                        <X className="h-4 w-4" />
                      </button>

                      {/* Candidate Avatar & Identity */}
                      <div className="flex items-start gap-2.5 pr-6 mb-2">
                        <div className="w-9 h-9 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shadow-sm shrink-0">
                          {mgr.name.charAt(0)}
                        </div>
                        <div className="min-w-0">
                          <h4 className="text-sm font-bold text-slate-900 truncate">
                            {mgr.name}
                          </h4>
                          <p className="text-xs text-slate-500 truncate">
                            {mgr.role_title || mgr.title || "Operations Leader"}
                          </p>
                          <p className="text-[11px] text-slate-400 truncate">
                            {mgr.location || "Pakistan"}
                          </p>
                        </div>
                      </div>

                      {/* Score Pill & Top Badge */}
                      <div className="mt-2.5 flex items-center justify-between gap-2">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border font-mono ${badgeColor}`}
                        >
                          <span>{score}% Match</span>
                        </span>
                        {isTop && (
                          <span className="text-[10px] font-bold uppercase text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            #1 Match
                          </span>
                        )}
                      </div>

                      {/* Action Button */}
                      <div className="mt-2.5">
                        <button
                          type="button"
                          onClick={() => onViewExplanation(cand)}
                          className="w-full inline-flex items-center justify-center gap-1 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 py-1.5 px-2 text-xs font-semibold shadow-sm transition-colors"
                        >
                          <Sparkles className="h-3 w-3 text-indigo-600" />
                          <span>View Decision Card</span>
                        </button>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>

            <tbody>
              {/* SECTION: 6 Deterministic Factors */}
              <tr className="bg-slate-100/80 border-b border-slate-200">
                <td
                  colSpan={candidates.length + 1}
                  className="px-4 py-2 text-[11px] font-bold uppercase tracking-wider text-indigo-900"
                >
                  Deterministic Factor Overlap
                </td>
              </tr>

              {FACTORS.map((factor) => (
                <tr
                  key={factor.key}
                  className="border-b border-slate-100 hover:bg-slate-50/60 transition-colors"
                >
                  <td className="p-3 text-xs font-semibold text-slate-700 sticky left-0 z-10 bg-white border-r border-slate-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                    <div className="flex items-center justify-between">
                      <span>{factor.label}</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        ({factor.weight})
                      </span>
                    </div>
                  </td>
                  {candidates.map((cand) => {
                    const rawScore = resolveScore(factor, cand.factor_scores);
                    const score = Math.min(100, Math.max(0, Math.round(rawScore)));

                    const isStageLeader = factor.key === "stage_fit" && cand.manager.id === stageFitLeaderId;
                    const isIndustryLeader = factor.key === "industry_fit" && cand.manager.id === industryFitLeaderId;

                    return (
                      <td
                        key={cand.manager.id}
                        className={`p-3 border-r border-slate-100 align-middle ${
                          isStageLeader || isIndustryLeader ? "bg-indigo-50/30" : ""
                        }`}
                      >
                        <div className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-slate-900 font-mono">
                              {score}%
                            </span>
                            {isStageLeader && (
                              <span className="text-[10px] font-bold text-indigo-700 bg-indigo-100 px-1.5 py-0.2 rounded">
                                Leads Stage Fit
                              </span>
                            )}
                            {isIndustryLeader && (
                              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-1.5 py-0.2 rounded">
                                Domain Leader
                              </span>
                            )}
                          </div>
                          <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${factor.barColor} rounded-full transition-all duration-300`}
                              style={{ width: `${score}%` }}
                            />
                          </div>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))}

              {/* SECTION: Compensation & Practical Alignment */}
              <tr className="bg-slate-100/80 border-b border-slate-200">
                <td
                  colSpan={candidates.length + 1}
                  className="px-4 py-2 text-[11px] font-bold uppercase tracking-wider text-slate-800"
                >
                  Compensation &amp; Work Structure
                </td>
              </tr>

              {/* Highlighted Row: Monthly Rate vs Budget Ceiling */}
              <tr className="border-b border-slate-100 bg-slate-50/50">
                <td className="p-3 text-xs font-bold text-slate-900 sticky left-0 z-10 bg-slate-50 border-r border-slate-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                  <div>
                    <span>Rate vs. Budget Ceiling</span>
                    <span className="block text-[10px] text-slate-500 font-normal">
                      Ceiling: ${budgetCeiling.toLocaleString()}/mo
                    </span>
                  </div>
                </td>
                {candidates.map((cand) => {
                  const mgr = cand.manager;
                  const rate =
                    mgr.expected_salary ??
                    mgr.salary_expectation ??
                    mgr.monthly_rate_usd ??
                    0;
                  const delta = budgetCeiling - rate;
                  const isWithin = delta >= 0;

                  return (
                    <td
                      key={cand.manager.id}
                      className="p-3 border-r border-slate-100 align-middle"
                    >
                      <div className="font-mono text-sm font-bold text-slate-900">
                        ${rate.toLocaleString()}/mo
                      </div>
                      <div className="mt-1">
                        {isWithin ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            <span>Within Budget (-${delta.toLocaleString()})</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                            <AlertTriangle className="w-3 h-3 text-rose-600" />
                            <span>Over Budget (+${Math.abs(delta).toLocaleString()})</span>
                          </span>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>

              {/* Work Arrangement */}
              <tr className="border-b border-slate-100 hover:bg-slate-50/60 transition-colors">
                <td className="p-3 text-xs font-semibold text-slate-700 sticky left-0 z-10 bg-white border-r border-slate-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                  Work Arrangement
                </td>
                {candidates.map((cand) => {
                  const mgr = cand.manager;
                  const arrangement =
                    mgr.work_arrangement || mgr.work_preference || "Not specified";
                  return (
                    <td
                      key={cand.manager.id}
                      className="p-3 text-xs text-slate-800 border-r border-slate-100 align-middle font-medium"
                    >
                      {arrangement}
                    </td>
                  );
                })}
              </tr>

              {/* Experience Years */}
              <tr className="border-b border-slate-100 hover:bg-slate-50/60 transition-colors">
                <td className="p-3 text-xs font-semibold text-slate-700 sticky left-0 z-10 bg-white border-r border-slate-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                  Years of Experience
                </td>
                {candidates.map((cand) => {
                  const mgr = cand.manager;
                  const exp =
                    mgr.experience_years ?? mgr.years_experience ?? "Not specified";
                  return (
                    <td
                      key={cand.manager.id}
                      className="p-3 text-xs text-slate-800 border-r border-slate-100 align-middle"
                    >
                      {typeof exp === "number" ? `${exp} years` : exp}
                    </td>
                  );
                })}
              </tr>

              {/* Core Competencies */}
              <tr className="border-b border-slate-100 hover:bg-slate-50/60 transition-colors">
                <td className="p-3 text-xs font-semibold text-slate-700 sticky left-0 z-10 bg-white border-r border-slate-200 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.05)]">
                  Top Competencies
                </td>
                {candidates.map((cand) => {
                  const skills = cand.manager.core_skills || cand.manager.skills || [];
                  return (
                    <td
                      key={cand.manager.id}
                      className="p-3 border-r border-slate-100 align-top"
                    >
                      <div className="flex flex-wrap gap-1">
                        {skills.slice(0, 4).map((s, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 border border-slate-200"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    </td>
                  );
                })}
              </tr>
            </tbody>
          </table>
        </div>

        {/* Modal Bottom Controls */}
        <div className="pt-4 border-t border-slate-200 flex items-center justify-between shrink-0">
          <span className="text-xs text-slate-500">
            Advisory decision-support matrix · Evaluated against business criteria
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            Done Comparing
          </button>
        </div>
      </div>
    </div>
  );
}
