"use client";

import React, { useEffect, useState } from "react";
import { FactorScores, MatchFactorScores } from "@/lib/types";

interface FactorProgressBarProps {
  factorScores: MatchFactorScores | FactorScores | Record<string, number | undefined>;
  compact?: boolean;
}

interface FactorMeta {
  key: string;
  aliases: string[];
  label: string;
  weight: string;
  barColor: string;
}

const FACTORS: FactorMeta[] = [
  {
    key: "skills_fit",
    aliases: ["skills", "skills_fit"],
    label: "Skills Fit",
    weight: "25%",
    barColor: "bg-indigo-600",
  },
  {
    key: "industry_fit",
    aliases: ["industry", "industry_fit"],
    label: "Industry Fit",
    weight: "20%",
    barColor: "bg-indigo-500",
  },
  {
    key: "experience_fit",
    aliases: ["experience", "experience_fit"],
    label: "Experience Fit",
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
    label: "Stage Fit",
    weight: "10%",
    barColor: "bg-violet-600",
  },
  {
    key: "salary_fit",
    aliases: ["salary", "salary_fit"],
    label: "Salary Fit",
    weight: "10%",
    barColor: "bg-amber-600",
  },
];

function resolveScore(
  factorMeta: FactorMeta,
  scores: Record<string, number | undefined>
): number {
  for (const alias of factorMeta.aliases) {
    if (typeof scores[alias] === "number") {
      return scores[alias]!;
    }
  }
  return 0;
}

export default function FactorProgressBar({
  factorScores,
  compact = false,
}: FactorProgressBarProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setMounted(true), 50);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="space-y-2 w-full">
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {FACTORS.map((factor) => {
          const rawScore = resolveScore(factor, factorScores);
          const score = Math.min(100, Math.max(0, Math.round(rawScore)));

          return (
            <div
              key={factor.key}
              className={`rounded-lg border border-slate-200 bg-slate-50/70 p-2 transition-all ${
                compact ? "p-1.5" : "p-2"
              }`}
            >
              <div className="flex items-center justify-between text-[11px] mb-1">
                <span className="text-slate-700 font-semibold truncate">
                  {factor.label}
                </span>
                <span className="font-mono text-slate-900 font-bold text-[11px] ml-1">
                  {score}%
                </span>
              </div>

              {/* Mini Animated Progress Bar */}
              <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${factor.barColor} rounded-full transition-all duration-700 ease-out`}
                  style={{ width: mounted ? `${score}%` : "0%" }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
