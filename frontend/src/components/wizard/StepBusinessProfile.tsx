"use client";

import React from "react";
import { Building2, MapPin, Users } from "lucide-react";
import { WizardFormData } from "./types";

interface StepBusinessProfileProps {
  data: WizardFormData;
  onChange: (updates: Partial<WizardFormData>) => void;
  errors?: Record<string, string>;
}

const STAGE_OPTIONS = [
  { label: "Early / Idea", value: "Early/Idea", desc: "0-1 product phase" },
  { label: "Seed Stage", value: "Seed", desc: "Initial traction" },
  { label: "Growth", value: "Growth", desc: "Scaling operations & teams" },
  { label: "Scaling / Series A+", value: "Scaling", desc: "Rapid market expansion" },
];

const BUSINESS_MODEL_SUGGESTIONS = [
  "Online Retail",
  "B2B SaaS",
  "Marketplace",
  "Direct-to-Consumer (D2C)",
  "Agency / Services",
  "FinTech",
];

const SIZE_OPTIONS = [
  { label: "Small (1–20)", value: "Small" },
  { label: "Medium (21–100)", value: "Medium" },
  { label: "Scaling (100+)", value: "Large" },
];

export default function StepBusinessProfile({
  data,
  onChange,
  errors = {},
}: StepBusinessProfileProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              1. Business Profile
            </h2>
            <p className="text-xs text-slate-500">
              Basic company firmographics and business stage classification.
            </p>
          </div>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600 border border-slate-200">
          Step 1 of 3
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Company Name */}
        <div>
          <label
            htmlFor="company-name"
            className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider"
          >
            Company Name <span className="text-rose-500">*</span>
          </label>
          <input
            id="company-name"
            type="text"
            required
            value={data.name}
            onChange={(e) => onChange({ name: e.target.value })}
            placeholder="e.g. FashionCart"
            className={`w-full bg-white border rounded-lg px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
              errors.name
                ? "border-rose-300 focus:border-rose-500 focus:ring-rose-200"
                : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-100"
            }`}
          />
          {errors.name && (
            <p className="text-xs text-rose-600 mt-1 font-medium">{errors.name}</p>
          )}
        </div>

        {/* Industry */}
        <div>
          <label
            htmlFor="industry"
            className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider"
          >
            Industry <span className="text-rose-500">*</span>
          </label>
          <input
            id="industry"
            type="text"
            required
            value={data.industry}
            onChange={(e) => onChange({ industry: e.target.value })}
            placeholder="e.g. E-commerce Apparel, B2B Logistics"
            className={`w-full bg-white border rounded-lg px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
              errors.industry
                ? "border-rose-300 focus:border-rose-500 focus:ring-rose-200"
                : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-100"
            }`}
          />
          {errors.industry && (
            <p className="text-xs text-rose-600 mt-1 font-medium">{errors.industry}</p>
          )}
        </div>

        {/* Location */}
        <div>
          <label
            htmlFor="company-location"
            className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider"
          >
            Operating Headquarters / Location
          </label>
          <div className="relative">
            <input
              id="company-location"
              type="text"
              value={data.location}
              onChange={(e) => onChange({ location: e.target.value })}
              placeholder="e.g. Lahore, Pakistan"
              className="w-full bg-white border border-slate-300 rounded-lg pl-9 pr-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition-all"
            />
            <MapPin className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
          </div>
        </div>

        {/* Employee Count */}
        <div>
          <label
            htmlFor="employee-count"
            className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider"
          >
            Total Employees <span className="text-rose-500">*</span>
          </label>
          <div className="relative">
            <input
              id="employee-count"
              type="number"
              min="1"
              required
              value={data.employee_count || ""}
              onChange={(e) =>
                onChange({ employee_count: parseInt(e.target.value, 10) || 0 })
              }
              placeholder="e.g. 12"
              className={`w-full bg-white border rounded-lg pl-9 pr-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                errors.employee_count
                  ? "border-rose-300 focus:border-rose-500 focus:ring-rose-200"
                  : "border-slate-300 focus:border-indigo-500 focus:ring-indigo-100"
              }`}
            />
            <Users className="w-4 h-4 text-slate-400 absolute left-3 top-3 pointer-events-none" />
          </div>
          {errors.employee_count && (
            <p className="text-xs text-rose-600 mt-1 font-medium">
              {errors.employee_count}
            </p>
          )}
        </div>
      </div>

      {/* Business Model Suggestion Chips */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 mb-2 uppercase tracking-wider">
          Primary Business Model
        </label>
        <div className="flex flex-wrap gap-2">
          {BUSINESS_MODEL_SUGGESTIONS.map((model) => {
            const isSelected = data.business_model === model;
            return (
              <button
                key={model}
                type="button"
                onClick={() => onChange({ business_model: model })}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                  isSelected
                    ? "bg-indigo-50 border-indigo-400 text-indigo-700 shadow-sm"
                    : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                }`}
              >
                {model}
              </button>
            );
          })}
        </div>
      </div>

      {/* Growth Stage Selector (Tactile Cards) */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 mb-2 uppercase tracking-wider">
          Lifecycle &amp; Growth Stage <span className="text-rose-500">*</span>
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {STAGE_OPTIONS.map((opt) => {
            const isSelected = data.stage === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange({ stage: opt.value })}
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
                    {opt.label}
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
                <p className="text-[11px] text-slate-500 leading-snug">{opt.desc}</p>
              </button>
            );
          })}
        </div>
        {errors.stage && (
          <p className="text-xs text-rose-600 mt-1.5 font-medium">{errors.stage}</p>
        )}
      </div>

      {/* Company Size Segmented Selection */}
      <div>
        <label className="block text-xs font-semibold text-slate-700 mb-2 uppercase tracking-wider">
          Team Size Bracket
        </label>
        <div className="grid grid-cols-3 gap-2 sm:gap-3">
          {SIZE_OPTIONS.map((opt) => {
            const isSelected = data.size === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange({ size: opt.value })}
                className={`py-2 px-3 rounded-lg border text-center text-xs font-semibold transition-all ${
                  isSelected
                    ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                    : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
                }`}
              >
                {opt.label}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
