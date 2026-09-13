"use client";

import React, { useState } from "react";
import { Zap, CheckCircle2, Sparkles, Loader2, AlertCircle } from "lucide-react";
import { getFashionCartDemoData } from "@/lib/api";

export interface DemoPresetData {
  name: string;
  industry: string;
  size: string;
  stage: string;
  location: string;
  employee_count: number;
  business_model: string;
  goals: string;
  challenges: string;
  required_skills: string[];
  salary_budget: number;
  work_arrangement: string;
}

interface DemoPresetButtonProps {
  onLoadPreset: (preset: DemoPresetData) => void;
  onInstantAnalyze?: () => void;
  isLoaded?: boolean;
}

export default function DemoPresetButton({
  onLoadPreset,
  onInstantAnalyze,
  isLoaded = false,
}: DemoPresetButtonProps) {
  const [justClicked, setJustClicked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleClick = async () => {
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const data = await getFashionCartDemoData();
      const preset: DemoPresetData = {
        name: data.name,
        industry: data.industry,
        size: data.size || "Small",
        stage: data.stage || "Growth",
        location: data.location || "Lahore, Pakistan",
        employee_count: data.employee_count || 12,
        business_model: data.business_model || "Online Retail",
        goals: data.goals || "",
        challenges: data.challenges || data.core_problem || "",
        required_skills: data.required_skills || ["Operations Management", "Process Optimization", "Team Management", "Supply Chain"],
        salary_budget: data.salary_budget || data.monthly_budget_usd || 2000,
        work_arrangement: data.work_arrangement || "Hybrid",
      };

      onLoadPreset(preset);
      setJustClicked(true);
      setTimeout(() => {
        setJustClicked(false);
      }, 2800);
    } catch (err) {
      console.error("Failed to load demo preset from API:", err);
      setErrorMsg("Failed to connect to backend demo endpoint.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full mb-6">
      <div className="relative overflow-hidden rounded-xl border border-amber-200 bg-amber-50/70 p-4 shadow-sm transition-all hover:border-amber-300">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-amber-100 text-amber-800 border border-amber-200 shadow-sm">
              <Zap className={`h-5 w-5 transition-transform duration-300 ${justClicked ? "scale-125 text-amber-600" : ""}`} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-900">
                  Live Backend Demo Scenario
                </span>
                <span className="rounded-full bg-white px-2 py-0.5 text-[10px] font-semibold text-amber-800 border border-amber-200">
                  GET /api/demo/fashioncart
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-0.5">
                Load the real <strong className="text-slate-900 font-semibold">FashionCart</strong> growth scenario directly from the running FastAPI backend.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              id="demo-preset-btn"
              onClick={handleClick}
              disabled={isLoading}
              className={`group inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-xs font-bold tracking-wide transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 ${
                isLoaded || justClicked
                  ? "bg-emerald-50 text-emerald-700 border border-emerald-300"
                  : "bg-indigo-600 hover:bg-indigo-700 text-white"
              } disabled:opacity-50`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Fetching Preset...</span>
                </>
              ) : isLoaded || justClicked ? (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                  <span>Preset Loaded ✓</span>
                </>
              ) : (
                <>
                  <Zap className="h-3.5 w-3.5 fill-current" />
                  <span>⚡ Load FashionCart Demo Scenario</span>
                </>
              )}
            </button>

            {onInstantAnalyze && (
              <button
                type="button"
                id="instant-analyze-btn"
                onClick={onInstantAnalyze}
                className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 px-3 py-2 text-xs font-semibold transition-all shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
                title="Immediately run live AI analysis and ranking"
              >
                <Sparkles className="h-3.5 w-3.5 text-indigo-600" />
                <span>Run Instant Match</span>
              </button>
            )}
          </div>
        </div>

        {errorMsg && (
          <div className="mt-2.5 p-2 rounded-lg bg-rose-50 border border-rose-200 flex items-center gap-2 text-xs text-rose-700">
            <AlertCircle className="w-3.5 h-3.5 shrink-0 text-rose-600" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>
    </div>
  );
}
