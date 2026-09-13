"use client";

import React, { useEffect } from "react";
import {
  X,
  Briefcase,
  Clock,
  Award,
  Trophy,
  DollarSign,
} from "lucide-react";
import { MatchRecord } from "@/lib/types";
import FactorProgressBar from "./FactorProgressBar";
import AiDecisionCard, { AiExplanationPayload } from "./AiDecisionCard";

interface CandidateDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  match: MatchRecord | null;
  explanation: AiExplanationPayload | null;
  isLoadingExplanation?: boolean;
}

export default function CandidateDetailModal({
  isOpen,
  onClose,
  match,
  explanation,
  isLoadingExplanation = false,
}: CandidateDetailModalProps) {
  // Escape key listener & body scroll lock
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = originalOverflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen || !match) return null;

  const mgr = match.manager;
  const overallScore = Math.min(100, Math.max(0, Math.round(match.overall_score)));
  const roleTitle = mgr.role_title || mgr.title || "Operations Leader";
  const location = mgr.location || "Not specified in profile";

  const experienceYears =
    typeof mgr.experience_years === "number"
      ? `${mgr.experience_years} years`
      : typeof mgr.years_experience === "number"
      ? `${mgr.years_experience} years`
      : "Not specified";

  const salary =
    typeof mgr.expected_salary === "number"
      ? `$${mgr.expected_salary.toLocaleString()}/mo`
      : typeof mgr.salary_expectation === "number"
      ? `$${mgr.salary_expectation.toLocaleString()}/mo`
      : typeof mgr.monthly_rate_usd === "number"
      ? `$${mgr.monthly_rate_usd.toLocaleString()}/mo`
      : "Not specified";

  const workArrangement =
    mgr.work_arrangement || mgr.work_preference || "Not specified";
  const availability = mgr.availability || "Immediate";

  const skills = mgr.core_skills || mgr.skills || [];
  const achievements = mgr.achievements || [];
  const teamTrackRecord =
    mgr.management_experience ||
    mgr.verified_track_record ||
    "Proven team leadership and cross-functional execution in fast-growing organizations.";

  let badgeStyle = "bg-slate-100 text-slate-700 border-slate-200";
  if (overallScore >= 85) {
    badgeStyle = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (overallScore >= 70) {
    badgeStyle = "bg-amber-50 text-amber-700 border-amber-200";
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop overlay with blur */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity duration-300 animate-fadeIn"
      />

      {/* Slide-over Drawer Container (Right side on desktop, bottom sheet on mobile) */}
      <div
        className="relative z-50 w-full sm:max-w-2xl lg:max-w-3xl bg-white shadow-2xl border-l border-slate-200 flex flex-col h-full overflow-hidden animate-in slide-in-from-right duration-300"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-candidate-name"
      >
        {/* Sticky Top Drawer Header */}
        <div className="p-5 sm:p-6 border-b border-slate-200 bg-white sticky top-0 z-10 flex items-start justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-sm shrink-0">
              {mgr.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2
                  id="modal-candidate-name"
                  className="text-lg sm:text-xl font-bold text-slate-900"
                >
                  {mgr.name}
                </h2>
                <div
                  className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-xs font-bold ${badgeStyle}`}
                >
                  <Award className="w-3.5 h-3.5" />
                  <span>{overallScore}% Match</span>
                </div>
              </div>
              <p className="text-xs sm:text-sm text-slate-600 font-medium mt-0.5">
                {roleTitle} · {location}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            aria-label="Close drawer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Drawer Content */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Experience</span>
              <span className="text-xs font-bold text-slate-900 flex items-center gap-1 mt-0.5">
                <Briefcase className="w-3.5 h-3.5 text-slate-500" />
                {experienceYears}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Monthly Rate</span>
              <span className="text-xs font-bold text-indigo-700 font-mono flex items-center gap-1 mt-0.5">
                <DollarSign className="w-3.5 h-3.5 text-indigo-600" />
                {salary}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Arrangement</span>
              <span className="text-xs font-bold text-slate-900 flex items-center gap-1 mt-0.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                {workArrangement}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
              <span className="text-[10px] text-slate-500 uppercase font-semibold block">Availability</span>
              <span className="text-xs font-bold text-emerald-700 flex items-center gap-1 mt-0.5">
                {availability}
              </span>
            </div>
          </div>

          {/* 6-Factor Deterministic Breakdown */}
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
              6-Factor Deterministic Compatibility Breakdown
            </h3>
            <FactorProgressBar factorScores={match.factor_scores} />
          </div>

          {/* AI Decision Card (Screen 8: Explainable 4-Quadrants & Strategic Verdict) */}
          <div className="p-4 sm:p-5 rounded-xl bg-white border border-slate-200 shadow-sm">
            <AiDecisionCard
              explanation={explanation}
              candidateName={mgr.name}
              overallScore={overallScore}
              isLoading={isLoadingExplanation}
            />
          </div>

          {/* Core Skills */}
          {skills && skills.length > 0 && (
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                Core Competencies &amp; Verified Skills
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-800 text-xs font-medium border border-slate-200"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Proven Track Record & Management Experience */}
          <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-1.5">
              Team Scale &amp; Leadership Experience
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {teamTrackRecord}
            </p>
          </div>

          {/* Verified Achievements */}
          {achievements && achievements.length > 0 && (
            <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                Key Accomplishments
              </h3>
              <ul className="space-y-2">
                {achievements.map((ach, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-slate-600">
                    <Trophy className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
                    <span>{ach}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Sticky Drawer Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between gap-3">
          <span className="text-xs text-slate-500">
            Advisory decision-support audit
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            Close Drawer
          </button>
        </div>
      </div>
    </div>
  );
}
