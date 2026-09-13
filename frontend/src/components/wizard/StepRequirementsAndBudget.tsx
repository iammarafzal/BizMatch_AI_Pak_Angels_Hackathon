"use client";

import React, { useState } from "react";
import { X, Award } from "lucide-react";
import { WizardFormData } from "./types";

interface StepRequirementsAndBudgetProps {
  data: WizardFormData;
  onChange: (updates: Partial<WizardFormData>) => void;
  errors?: Record<string, string>;
}

const QUICK_SKILL_PILLS = [
  "Operations",
  "Scaling",
  "Logistics",
  "E-commerce",
  "Team Leadership",
  "Finance",
  "Process Optimization",
  "Supply Chain",
  "Inventory Management",
  "Growth Strategy",
];

const WORK_ARRANGEMENTS = [
  { value: "Remote", label: "Remote", desc: "Global / Distributed" },
  { value: "Hybrid", label: "Hybrid", desc: "Flexible in-office + remote" },
  { value: "On-site", label: "On-site", desc: "Full-time at facility" },
];

const BUDGET_PRESETS = [1500, 2000, 2500, 3000, 4000];

export default function StepRequirementsAndBudget({
  data,
  onChange,
  errors = {},
}: StepRequirementsAndBudgetProps) {
  const [customTagInput, setCustomTagInput] = useState("");

  const handleAddSkill = (skill: string) => {
    const trimmed = skill.trim();
    if (!trimmed) return;
    if (!data.required_skills.some((s) => s.toLowerCase() === trimmed.toLowerCase())) {
      onChange({
        required_skills: [...data.required_skills, trimmed],
      });
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    onChange({
      required_skills: data.required_skills.filter(
        (s) => s.toLowerCase() !== skillToRemove.toLowerCase()
      ),
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      handleAddSkill(customTagInput);
      setCustomTagInput("");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              3. Manager Requirements &amp; Compensation
            </h2>
            <p className="text-xs text-slate-500">
              Deterministic factor filters: required competencies, monthly budget ceiling, and workspace setup.
            </p>
          </div>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600 border border-slate-200">
          Step 3 of 3
        </span>
      </div>

      <div className="space-y-6">
        {/* Monthly Salary Budget Ceiling */}
        <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 sm:p-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
            <div>
              <label
                htmlFor="salary-budget-input"
                className="block text-xs font-semibold text-slate-700 uppercase tracking-wider"
              >
                Monthly Compensation Budget Ceiling (USD) <span className="text-rose-500">*</span>
              </label>
              <p className="text-[11px] text-slate-500">
                Determines deterministic salary fit score against candidate rate expectations.
              </p>
            </div>
            <div className="flex items-center gap-1 font-mono text-lg font-bold text-slate-900">
              <span>$</span>
              <span>{(data.salary_budget || 0).toLocaleString()}</span>
              <span className="text-xs text-slate-500 font-sans font-normal">/mo</span>
            </div>
          </div>

          <div className="space-y-3">
            <div className="relative flex items-center">
              <input
                id="salary-budget-slider"
                type="range"
                min="800"
                max="6000"
                step="100"
                value={data.salary_budget || 2000}
                onChange={(e) =>
                  onChange({ salary_budget: parseInt(e.target.value, 10) })
                }
                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              <div className="flex items-center gap-1.5">
                <span className="text-[11px] text-slate-500">Quick ceiling:</span>
                {BUDGET_PRESETS.map((val) => (
                  <button
                    key={val}
                    type="button"
                    onClick={() => onChange({ salary_budget: val })}
                    className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-all border ${
                      data.salary_budget === val
                        ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                        : "bg-white border-slate-300 text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    ${val.toLocaleString()}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-1.5">
                <span className="text-xs text-slate-500">Manual: $</span>
                <input
                  id="salary-budget-input"
                  type="number"
                  min="100"
                  step="50"
                  value={data.salary_budget || ""}
                  onChange={(e) =>
                    onChange({ salary_budget: parseInt(e.target.value, 10) || 0 })
                  }
                  className="w-24 bg-white border border-slate-300 rounded-md px-2 py-1 text-xs font-mono text-slate-900 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>
          {errors.salary_budget && (
            <p className="text-xs text-rose-600 mt-2 font-medium">
              {errors.salary_budget}
            </p>
          )}
        </div>

        {/* Required Manager Skills / Tag Input */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
            Required Competencies &amp; Skills <span className="text-rose-500">*</span>
          </label>
          <p className="text-xs text-slate-500 mb-3">
            Managers with overlapping skills receive higher deterministic skills-fit scores.
          </p>

          {/* Selected Skills Chips */}
          <div className="min-h-[50px] p-2.5 rounded-lg border border-slate-300 bg-white flex flex-wrap gap-2 items-center mb-3">
            {data.required_skills.length === 0 ? (
              <span className="text-xs text-slate-400 pl-1">
                No skills selected yet. Click from recommendations below or type and press Enter.
              </span>
            ) : (
              data.required_skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-indigo-50 text-indigo-800 text-xs font-medium border border-indigo-200"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    className="text-indigo-600 hover:text-indigo-900 focus:outline-none"
                    title={`Remove ${skill}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))
            )}
          </div>

          {/* Custom Tag Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={customTagInput}
              onChange={(e) => setCustomTagInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a skill and press Enter (e.g. Supply Chain, Shopify Plus)"
              className="flex-grow bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-100 focus:border-indigo-500"
            />
            <button
              type="button"
              onClick={() => {
                handleAddSkill(customTagInput);
                setCustomTagInput("");
              }}
              className="px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold border border-slate-300 transition-colors"
            >
              Add Skill
            </button>
          </div>

          {/* Recommended Quick Skills Pills */}
          <div className="mt-3 flex flex-wrap gap-1.5">
            {QUICK_SKILL_PILLS.map((skill) => {
              const isAdded = data.required_skills.some(
                (s) => s.toLowerCase() === skill.toLowerCase()
              );
              return (
                <button
                  key={skill}
                  type="button"
                  onClick={() =>
                    isAdded ? handleRemoveSkill(skill) : handleAddSkill(skill)
                  }
                  className={`text-xs px-2.5 py-1 rounded-md transition-all border ${
                    isAdded
                      ? "bg-indigo-600 text-white border-indigo-600 font-semibold"
                      : "bg-white border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  {isAdded ? `✓ ${skill}` : `+ ${skill}`}
                </button>
              );
            })}
          </div>
          {errors.required_skills && (
            <p className="text-xs text-rose-600 mt-1.5 font-medium">
              {errors.required_skills}
            </p>
          )}
        </div>

        {/* Work Arrangement Selector (Tactile Segmented Radio Cards) */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-2 uppercase tracking-wider">
            Operational Work Arrangement <span className="text-rose-500">*</span>
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {WORK_ARRANGEMENTS.map((item) => {
              const isSelected = data.work_arrangement === item.value;
              return (
                <button
                  key={item.value}
                  type="button"
                  onClick={() => onChange({ work_arrangement: item.value })}
                  className={`p-3.5 rounded-lg border text-left transition-all ${
                    isSelected
                      ? "bg-indigo-50/70 border-indigo-500 ring-1 ring-indigo-500 shadow-sm"
                      : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span
                      className={`text-xs font-bold ${
                        isSelected ? "text-indigo-900" : "text-slate-900"
                      }`}
                    >
                      {item.label}
                    </span>
                    <div
                      className={`w-3.5 h-3.5 rounded-full border flex items-center justify-center ${
                        isSelected
                          ? "border-indigo-600 bg-indigo-600"
                          : "border-slate-300"
                      }`}
                    >
                      {isSelected && (
                        <div className="w-1.5 h-1.5 bg-white rounded-full" />
                      )}
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-500">{item.desc}</p>
                </button>
              );
            })}
          </div>
          {errors.work_arrangement && (
            <p className="text-xs text-rose-600 mt-1.5 font-medium">
              {errors.work_arrangement}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
