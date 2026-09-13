"use client";

import React from "react";
import { Target, AlertTriangle, Lightbulb } from "lucide-react";
import { WizardFormData } from "./types";

interface StepGoalsAndChallengesProps {
  data: WizardFormData;
  onChange: (updates: Partial<WizardFormData>) => void;
  errors?: Record<string, string>;
}

const COMMON_CHALLENGE_PROMPTS = [
  "Inventory discrepancies between Shopify and warehouse physical stock",
  "Customer service delays exceeding 24h SLA during peak sale campaigns",
  "High 3PL fulfillment costs and lack of batch shipping automation",
  "Founder bottleneck: spending 80% time on daily firefighting instead of growth",
];

const COMMON_GOAL_PROMPTS = [
  "Double monthly GMV while keeping operational overhead under 15%",
  "Scale warehouse operations from 50 to 500 daily shipments",
  "Automate inventory forecasting and reduce stockouts by 80%",
];

export default function StepGoalsAndChallenges({
  data,
  onChange,
  errors = {},
}: StepGoalsAndChallengesProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              2. Goals &amp; Operational Bottlenecks
            </h2>
            <p className="text-xs text-slate-500">
              BizMatch AI extracts critical priorities from your real challenges to ground deterministic factor scoring.
            </p>
          </div>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600 border border-slate-200">
          Step 2 of 3
        </span>
      </div>

      {/* Strategic Goals Textarea */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label
            htmlFor="company-goals"
            className="block text-xs font-semibold text-slate-700 uppercase tracking-wider"
          >
            Core Business Goals (Next 6–12 Months) <span className="text-rose-500">*</span>
          </label>
          <span className="text-[11px] text-slate-400 font-mono">
            {data.goals.length} characters
          </span>
        </div>
        <textarea
          id="company-goals"
          rows={3}
          required
          value={data.goals}
          onChange={(e) => onChange({ goals: e.target.value })}
          placeholder="e.g. Expand e-commerce orders from 50/day to 500/day, launch 2 new apparel collections, and achieve profitability within 6 months."
          className={`w-full bg-white border rounded-lg p-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
            errors.goals
              ? "border-rose-300 focus:border-rose-500 focus:ring-rose-200"
              : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-100"
          }`}
        />
        {errors.goals && (
          <p className="text-xs text-rose-600 mt-1 font-medium">{errors.goals}</p>
        )}

        {/* Quick Goal Starters */}
        <div className="mt-2 flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] text-slate-400 flex items-center gap-1 mr-1">
            <Lightbulb className="w-3 h-3 text-amber-500" /> Starters:
          </span>
          {COMMON_GOAL_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => {
                const combined = data.goals ? `${data.goals} ${prompt}` : prompt;
                onChange({ goals: combined });
              }}
              className="text-[11px] rounded-md bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-slate-600 px-2 py-0.5 border border-slate-200 transition-colors"
            >
              + {prompt.slice(0, 35)}...
            </button>
          ))}
        </div>
      </div>

      {/* Operational Challenges Textarea */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <label
            htmlFor="company-challenges"
            className="block text-xs font-semibold text-slate-700 uppercase tracking-wider"
          >
            Operational Bottlenecks &amp; Problems <span className="text-rose-500">*</span>
          </label>
          <span className="text-[11px] text-slate-400 font-mono">
            {data.challenges.length} characters
          </span>
        </div>
        <textarea
          id="company-challenges"
          rows={4}
          required
          value={data.challenges}
          onChange={(e) => onChange({ challenges: e.target.value })}
          placeholder="e.g. Stock counts don't match between website and warehouse, high return rates due to wrong sizes sent, warehouse staff untrained on Shopify Plus and 3PL software."
          className={`w-full bg-white border rounded-lg p-3 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
            errors.challenges
              ? "border-rose-300 focus:border-rose-500 focus:ring-rose-200"
              : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-100"
          }`}
        />
        {errors.challenges && (
          <p className="text-xs text-rose-600 mt-1 font-medium">{errors.challenges}</p>
        )}

        {/* Quick Challenge Starters */}
        <div className="mt-2.5">
          <p className="text-[11px] font-semibold text-slate-500 mb-1.5 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-amber-500" /> Click to add common bottlenecks:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {COMMON_CHALLENGE_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => {
                  const current = data.challenges.trim();
                  const updated = current ? `${current}\n• ${prompt}` : `• ${prompt}`;
                  onChange({ challenges: updated });
                }}
                className="text-left text-[11px] rounded-lg bg-slate-50 hover:bg-indigo-50/70 hover:border-indigo-300 text-slate-700 p-2 border border-slate-200 transition-colors"
              >
                + {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
