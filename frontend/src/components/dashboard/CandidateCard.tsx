"use client";

import React from "react";
import {
  MapPin,
  Briefcase,
  DollarSign,
  Clock,
  Award,
  ArrowRight,
} from "lucide-react";
import { MatchRecord } from "@/lib/types";
import FactorProgressBar from "./FactorProgressBar";

interface CandidateCardProps {
  match: MatchRecord;
  rank: number;
  isSelectedForCompare: boolean;
  onToggleCompare: (candidateId: string) => void;
  onViewExplanation: (match: MatchRecord) => void;
}

export default function CandidateCard({
  match,
  rank,
  isSelectedForCompare,
  onToggleCompare,
  onViewExplanation,
}: CandidateCardProps) {
  const mgr = match.manager;
  const overallScore = Math.min(100, Math.max(0, Math.round(match.overall_score)));

  // Color Rules for Overall Score:
  // >= 85%: bg-emerald-50 text-emerald-700 border-emerald-200
  // 70% - 84%: bg-amber-50 text-amber-700 border-amber-200
  // < 70%: bg-slate-100 text-slate-700 border-slate-200
  let badgeStyle = "bg-slate-100 text-slate-700 border-slate-200";
  let badgeLabel = "Baseline Fit";

  if (overallScore >= 85) {
    badgeStyle = "bg-emerald-50 text-emerald-700 border-emerald-200";
    badgeLabel = "High Fit Match";
  } else if (overallScore >= 70) {
    badgeStyle = "bg-amber-50 text-amber-700 border-amber-200";
    badgeLabel = "Moderate Fit";
  }

  const roleTitle = mgr.role_title || mgr.title || "Operations Leader";
  const location = mgr.location || "Not provided";
  const experienceYears =
    typeof mgr.experience_years === "number"
      ? mgr.experience_years
      : typeof mgr.years_experience === "number"
      ? mgr.years_experience
      : "Not provided";

  const salary =
    typeof mgr.expected_salary === "number"
      ? `$${mgr.expected_salary.toLocaleString()}/mo`
      : typeof mgr.salary_expectation === "number"
      ? `$${mgr.salary_expectation.toLocaleString()}/mo`
      : typeof mgr.monthly_rate_usd === "number"
      ? `$${mgr.monthly_rate_usd.toLocaleString()}/mo`
      : "Not provided";

  const workArrangement =
    mgr.work_arrangement || mgr.work_preference || "Not provided";

  const skills = mgr.core_skills || mgr.skills || [];

  return (
    <div
      className={`bg-white rounded-xl border p-5 sm:p-6 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between overflow-hidden ${
        rank === 1
          ? "border-indigo-300 ring-1 ring-indigo-200"
          : isSelectedForCompare
          ? "border-indigo-500 ring-2 ring-indigo-100"
          : "border-slate-200/90"
      }`}
    >
      <div>
        {/* Top Header Row */}
        <div className="flex items-start justify-between gap-3 pb-4 border-b border-slate-100">
          <div className="flex items-start gap-3 min-w-0 flex-1">
            {/* Rank Badge */}
            <div
              className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg font-bold text-xs shadow-sm ${
                rank === 1
                  ? "bg-indigo-600 text-white"
                  : rank <= 3
                  ? "bg-slate-100 text-slate-800 border border-slate-200"
                  : "bg-slate-50 text-slate-500 border border-slate-200"
              }`}
            >
              #{rank}
            </div>

            {/* Candidate Identity */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 min-w-0">
                <h3 className="text-base font-bold text-slate-900 truncate" title={mgr.name}>
                  {mgr.name}
                </h3>
                {rank === 1 && (
                  <span className="hidden sm:inline-block px-1.5 py-0.5 rounded text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 shrink-0">
                    Top Pick
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-600 font-medium truncate mt-0.5" title={roleTitle}>
                {roleTitle}
              </p>
            </div>
          </div>

          {/* Immediate Overall Score Pill */}
          <div className="shrink-0 text-right pl-2">
            <div
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full border text-xs font-bold whitespace-nowrap shadow-sm ${badgeStyle}`}
            >
              <Award className="w-3.5 h-3.5 shrink-0" />
              <span>{overallScore}%</span>
            </div>
            <span className="text-[10px] text-slate-400 block mt-0.5 whitespace-nowrap">
              {badgeLabel}
            </span>
          </div>
        </div>

        {/* Quick Firmographic Data Row */}
        <div className="grid grid-cols-2 gap-2 my-3 text-xs text-slate-600">
          <div className="flex items-center gap-1.5 min-w-0 truncate" title={`${experienceYears} yrs experience`}>
            <Briefcase className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{experienceYears} yrs experience</span>
          </div>

          <div className="flex items-center gap-1.5 min-w-0 truncate" title={location}>
            <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{location}</span>
          </div>

          <div className="flex items-center gap-1.5 min-w-0 truncate font-medium text-slate-900" title={salary}>
            <DollarSign className="w-3.5 h-3.5 text-indigo-600 shrink-0" />
            <span className="truncate">{salary}</span>
          </div>

          <div className="flex items-center gap-1.5 min-w-0 truncate" title={workArrangement}>
            <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{workArrangement}</span>
          </div>
        </div>

        {/* 6-Factor Deterministic Mini Progress Bars */}
        <div className="pt-2 pb-3 border-t border-slate-100">
          <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
            <span>6-Factor Deterministic Score</span>
          </div>
          <FactorProgressBar factorScores={match.factor_scores} compact />
        </div>

        {/* Top Skill Tags (First 3) */}
        {skills && skills.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-4">
            {skills.slice(0, 3).map((skill, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200"
              >
                {skill}
              </span>
            ))}
            {skills.length > 3 && (
              <span className="px-1.5 py-0.5 text-[10px] text-slate-400">
                +{skills.length - 3} more
              </span>
            )}
          </div>
        )}
      </div>

      {/* Card Footer Actions */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
        {/* Comparison Checkbox */}
        <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 hover:text-indigo-600 select-none">
          <input
            type="checkbox"
            checked={isSelectedForCompare}
            onChange={() => onToggleCompare(mgr.id)}
            className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span>Compare</span>
        </label>

        {/* Primary Outline Button */}
        <button
          type="button"
          onClick={() => onViewExplanation(match)}
          className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50 px-3 py-1.5 rounded-lg border border-indigo-200 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
        >
          <span>Why This Candidate?</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}
