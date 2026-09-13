"use client";

import React, { useEffect, useState, useMemo, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Sparkles,
  Building2,
  DollarSign,
  TrendingUp,
  Layers,
  SlidersHorizontal,
  Columns3,
  X,
  Loader2,
  AlertCircle,
  RotateCcw,
  Edit3,
} from "lucide-react";
import CandidateCard from "@/components/dashboard/CandidateCard";
import CandidateDetailModal from "@/components/dashboard/CandidateDetailModal";
import CandidateComparisonTable from "@/components/dashboard/CandidateComparisonTable";
import { AiExplanationPayload } from "@/components/dashboard/AiDecisionCard";
import { CandidateMatchSummary, Business } from "@/types/api";
import { calculateMatches, getManagers, getCandidateExplanation } from "@/lib/api";

type SortOption = "overall" | "industry" | "salary";

function ResultsContent() {
  const searchParams = useSearchParams();
  const bizIdParam = searchParams.get("bizId");

  const [matches, setMatches] = useState<CandidateMatchSummary[]>([]);
  const [businessProfile, setBusinessProfile] = useState<Partial<Business> | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sortOption, setSortOption] = useState<SortOption>("overall");

  // Selection for comparison dock (up to 3 candidates)
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<string[]>([]);
  const [isComparisonMatrixOpen, setIsComparisonMatrixOpen] = useState(false);

  // Selected candidate for AI Decision Explanation modal/drawer
  const [activeExplanationMatch, setActiveExplanationMatch] = useState<CandidateMatchSummary | null>(null);
  const [explanationData, setExplanationData] = useState<AiExplanationPayload | null>(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  // Listen to compare URL search query if provided directly
  useEffect(() => {
    const compareParam = searchParams.get("compare");
    if (compareParam) {
      const ids = compareParam.split(",").filter(Boolean);
      if (ids.length >= 2) {
        setSelectedCandidateIds(ids.slice(0, 3));
        setIsComparisonMatrixOpen(true);
      }
    }
  }, [searchParams]);

  const loadDataForBusiness = async (targetBizId: string, currentBiz?: Partial<Business> | null) => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const [batchRes, managersList] = await Promise.all([
        calculateMatches(targetBizId),
        getManagers().catch(() => []),
      ]);

      if (batchRes && batchRes.matches && batchRes.matches.length > 0) {
        const enriched = batchRes.matches.map((m) => {
          const foundMgr = managersList.find((mgr) => mgr.id === m.manager.id);
          return {
            ...m,
            manager: {
              ...m.manager,
              ...(foundMgr || {}),
            },
          };
        });
        setMatches(enriched);
        if (typeof window !== "undefined") {
          sessionStorage.setItem("bizmatch_calculated_matches", JSON.stringify(enriched));
          if (currentBiz) {
            sessionStorage.setItem("bizmatch_business_data", JSON.stringify(currentBiz));
          }
        }
      } else {
        setMatches([]);
        setErrorMsg("No evaluated candidate matches returned for this business profile.");
      }
    } catch (err) {
      console.error("Failed to fetch fresh matches from backend:", err);
      const msg =
        err instanceof Error
          ? err.message
          : "Unable to calculate matches from backend. Please ensure the backend is running.";
      setErrorMsg(msg);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (typeof window === "undefined") return;

    async function hydrateDashboard() {
      const storedMatches = sessionStorage.getItem("bizmatch_calculated_matches");
      const storedBiz = sessionStorage.getItem("bizmatch_business_data");

      let activeBiz: Partial<Business> | null = null;
      if (storedBiz) {
        try {
          activeBiz = JSON.parse(storedBiz);
          setBusinessProfile(activeBiz);
        } catch {
          // ignore parsing error
        }
      }

      // If stored matches already exist in session, hydrate directly
      if (storedMatches) {
        try {
          const parsedMatches = JSON.parse(storedMatches) as CandidateMatchSummary[];
          if (Array.isArray(parsedMatches) && parsedMatches.length > 0) {
            setMatches(parsedMatches);
            setLoading(false);
            return;
          }
        } catch {
          // fallback to fresh API fetch
        }
      }

      // If direct access without session or params, render empty state
      if (!bizIdParam && !storedBiz) {
        setMatches([]);
        setLoading(false);
        return;
      }

      // Fetch directly from live backend
      const targetBizId = bizIdParam || "biz-fashioncart";
      await loadDataForBusiness(targetBizId, activeBiz);
    }

    hydrateDashboard();
  }, [bizIdParam]);

  // Load sample FashionCart results strictly from live API
  const handleLoadSampleResults = async () => {
    const demoBiz: Partial<Business> = {
      name: "FashionCart",
      industry: "Fashion E-commerce",
      stage: "Growth",
      salary_budget: 2000,
      location: "Lahore, Pakistan",
    };
    setBusinessProfile(demoBiz);
    await loadDataForBusiness("biz-fashioncart", demoBiz);
  };

  // Handle candidate selection for comparison dock
  const handleToggleCompare = (candidateId: string) => {
    setSelectedCandidateIds((prev) => {
      if (prev.includes(candidateId)) {
        return prev.filter((id) => id !== candidateId);
      }
      if (prev.length >= 3) {
        return [...prev.slice(1), candidateId];
      }
      return [...prev, candidateId];
    });
  };

  // Sorting logic
  const sortedMatches = useMemo(() => {
    const list = [...matches];
    if (sortOption === "industry") {
      return list.sort(
        (a, b) => (b.factor_scores.industry_fit ?? 0) - (a.factor_scores.industry_fit ?? 0)
      );
    }
    if (sortOption === "salary") {
      return list.sort(
        (a, b) => (b.factor_scores.salary_fit ?? 0) - (a.factor_scores.salary_fit ?? 0)
      );
    }
    return list.sort((a, b) => b.overall_score - a.overall_score);
  }, [matches, sortOption]);

  // AI Decision Support Deep-Dive via POST /api/matches/explain
  const handleViewExplanation = async (match: CandidateMatchSummary) => {
    setActiveExplanationMatch(match);
    setExplanationData(null);

    const mgrId = match.manager.id;
    const cacheKey = `bizmatch_exp_${mgrId}`;

    if (typeof window !== "undefined") {
      const cached = sessionStorage.getItem(cacheKey);
      if (cached) {
        try {
          setExplanationData(JSON.parse(cached));
          return;
        } catch {
          // ignore
        }
      }
    }

    if (match.explanation) {
      const exp = match.explanation;
      const parsed: AiExplanationPayload = {
        strengths: exp.strengths || [],
        concerns: exp.concerns || [],
        missing_requirements: exp.missing_requirements || [],
        verdict: exp.verdict || "",
      };
      setExplanationData(parsed);
      if (typeof window !== "undefined") {
        sessionStorage.setItem(cacheKey, JSON.stringify(parsed));
      }
      return;
    }

    const bizId = bizIdParam || "biz-fashioncart";
    setLoadingExplanation(true);

    try {
      const res = await getCandidateExplanation(bizId, mgrId, {
        name: businessProfile?.name || "FashionCart",
        industry: businessProfile?.industry || "Fashion E-commerce",
        stage: businessProfile?.stage || "Growth",
        salary_budget: businessProfile?.salary_budget || 2000,
        goals: businessProfile?.goals || "",
        challenges: businessProfile?.challenges || "",
      });

      let payload: AiExplanationPayload | null = null;
      if (res && res.data) {
        payload = {
          strengths: res.data.strengths || [],
          concerns: res.data.concerns || [],
          missing_requirements: res.data.missing_requirements || [],
          verdict: res.data.verdict || "",
        };
      } else if (res && res.strengths) {
        payload = {
          strengths: res.strengths || [],
          concerns: res.concerns || [],
          missing_requirements: res.missing_requirements || [],
          verdict: res.verdict || "",
        };
      }

      if (payload) {
        setExplanationData(payload);
        if (typeof window !== "undefined") {
          sessionStorage.setItem(cacheKey, JSON.stringify(payload));
        }
      }
    } catch (err) {
      console.error("API explanation call failed:", err);
      setExplanationData({
        strengths: [
          `Verified operational experience in ${(match.manager.industries || [])[0] || "industry scaling"}.`,
        ],
        concerns: [
          `Detailed explanation temporarily unavailable: ${err instanceof Error ? err.message : "API timeout"}.`,
        ],
        missing_requirements: [],
        verdict: `Candidate evaluated with ${Math.round(match.overall_score)}% deterministic score based on verified factor models.`,
      });
    } finally {
      setLoadingExplanation(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center p-6 text-center">
        <Loader2 className="w-10 h-10 animate-spin text-indigo-600 mb-3" />
        <h2 className="text-xl font-bold text-slate-900 mb-1">
          Loading Ranked Candidate Dashboard...
        </h2>
        <p className="text-xs text-slate-500">
          Calculating 6-factor deterministic scores via live FastAPI backend.
        </p>
      </div>
    );
  }

  // Error Banner if API call failed
  if (errorMsg && matches.length === 0) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center p-6 text-center max-w-md mx-auto">
        <div className="p-8 rounded-xl border border-rose-200 bg-white text-center shadow-sm w-full">
          <div className="w-12 h-12 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 mx-auto mb-4">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">
            Backend Connection Error
          </h2>
          <p className="text-xs text-slate-600 mb-6 leading-relaxed">
            {errorMsg}
          </p>
          <div className="flex flex-col gap-2.5">
            <button
              type="button"
              onClick={handleLoadSampleResults}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 text-xs font-bold transition-all shadow-sm"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Retry with FashionCart Scenario</span>
            </button>
            <Link
              href="/match"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 px-5 py-2.5 text-xs font-semibold transition-all"
            >
              <span>Back to Needs Wizard</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Empty state card
  if (matches.length === 0) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center p-6 text-center max-w-md mx-auto">
        <div className="p-8 rounded-xl border border-slate-200 bg-white text-center shadow-sm w-full">
          <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 mx-auto mb-4">
            <Building2 className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">
            No Active Match Records
          </h2>
          <p className="text-xs text-slate-500 mb-6 leading-relaxed">
            No candidate evaluation found. Load the live FashionCart demo scenario from the backend or configure a custom business profile.
          </p>
          <div className="flex flex-col gap-2.5">
            <button
              type="button"
              id="empty-state-load-sample-btn"
              onClick={handleLoadSampleResults}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 text-xs font-bold transition-all shadow-sm"
            >
              <Sparkles className="w-4 h-4" />
              <span>Load Sample Results (FashionCart)</span>
            </button>
            <Link
              href="/match"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 px-5 py-2.5 text-xs font-semibold transition-all"
            >
              <span>Launch Needs Wizard</span>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const selectedCandidates = matches.filter((m) =>
    selectedCandidateIds.includes(m.manager.id)
  );

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto pb-32">
      {/* Top Summary Header with Compact Firmographic Chip Bar & Edit Criteria */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 sm:p-6 shadow-sm mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-700">
                Evaluation Results
              </span>
              <span className="text-slate-300">•</span>
              <span className="text-xs text-slate-500 font-medium">
                {matches.length} candidates evaluated
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
              {businessProfile?.name || "FashionCart"}
            </h1>
          </div>

          {/* Compact Firmographic Chip Bar & Quick "Edit Criteria" Button */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
              <Layers className="w-3.5 h-3.5 text-indigo-600" />
              <span>{businessProfile?.industry || "Fashion E-commerce"}</span>
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
              <span>{businessProfile?.stage || "Growth"} Stage</span>
            </div>

            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 text-slate-900 text-xs font-bold font-mono border border-slate-200">
              <DollarSign className="w-3.5 h-3.5 text-indigo-600" />
              <span>${(businessProfile?.salary_budget || 2000).toLocaleString()}/mo</span>
            </div>

            <Link
              href="/match"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-indigo-600 text-xs font-semibold border border-indigo-200 shadow-sm transition-all ml-1"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Criteria</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Action Bar: Sort & Filter Controls & Compare Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 p-3.5 rounded-xl bg-white border border-slate-200 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-600 uppercase tracking-wider mr-1">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Sort:</span>
          </div>
          <button
            type="button"
            onClick={() => setSortOption("overall")}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              sortOption === "overall"
                ? "bg-indigo-600 text-white shadow-sm font-bold"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Overall Match (Default)
          </button>
          <button
            type="button"
            onClick={() => setSortOption("industry")}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              sortOption === "industry"
                ? "bg-indigo-600 text-white shadow-sm font-bold"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Industry Fit
          </button>
          <button
            type="button"
            onClick={() => setSortOption("salary")}
            className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              sortOption === "salary"
                ? "bg-indigo-600 text-white shadow-sm font-bold"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Salary Compatibility
          </button>
        </div>

        {/* Compare Selected Button */}
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            disabled={selectedCandidateIds.length < 2}
            onClick={() => {
              if (selectedCandidateIds.length >= 2) {
                setIsComparisonMatrixOpen(true);
              }
            }}
            className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm ${
              selectedCandidateIds.length >= 2
                ? "bg-indigo-600 hover:bg-indigo-700 text-white cursor-pointer"
                : "bg-slate-100 text-slate-400 border border-slate-200 cursor-not-allowed"
            }`}
          >
            <Columns3 className="w-3.5 h-3.5" />
            <span>Compare Selected</span>
            {selectedCandidateIds.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-white/20 text-white font-bold">
                {selectedCandidateIds.length}
              </span>
            )}
          </button>

          {selectedCandidateIds.length > 0 && (
            <button
              type="button"
              onClick={() => setSelectedCandidateIds([])}
              className="text-slate-500 hover:text-slate-800 text-xs font-medium underline"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Candidate Grid Layout: 1 col on mobile, 2 col on tablet/laptop, 3 col on large desktop */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {sortedMatches.map((match, idx) => (
          <CandidateCard
            key={match.manager.id || idx}
            match={match}
            rank={idx + 1}
            isSelectedForCompare={selectedCandidateIds.includes(match.manager.id)}
            onToggleCompare={handleToggleCompare}
            onViewExplanation={handleViewExplanation}
          />
        ))}
      </div>

      {/* Floating Comparison Action Dock */}
      {selectedCandidateIds.length >= 2 && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 w-11/12 max-w-xl animate-in slide-in-from-bottom-5 duration-200">
          <div className="rounded-xl border border-indigo-200 bg-white/95 p-3.5 shadow-xl backdrop-blur-md flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="flex -space-x-1.5 overflow-hidden">
                {selectedCandidates.map((c) => (
                  <div
                    key={c.manager.id}
                    className="inline-flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-indigo-600 text-xs font-bold text-white shadow-sm"
                    title={c.manager.name}
                  >
                    {c.manager.name.charAt(0)}
                  </div>
                ))}
              </div>
              <div className="text-left">
                <span className="text-xs font-bold text-slate-900 block">
                  {selectedCandidateIds.length} Candidates Selected
                </span>
                <span className="text-[11px] text-slate-500 block truncate max-w-[200px]">
                  {selectedCandidates.map((c) => c.manager.name).join(", ")}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <button
                type="button"
                onClick={() => setIsComparisonMatrixOpen(true)}
                className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 text-xs font-bold shadow-sm transition-all"
              >
                <Columns3 className="w-3.5 h-3.5" />
                <span>Compare Side-by-Side</span>
              </button>
              <button
                type="button"
                onClick={() => setSelectedCandidateIds([])}
                className="p-2 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-500 hover:text-slate-800 transition-colors"
                title="Deselect All"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Screen 9: Side-by-Side Candidate Comparison Matrix */}
      {isComparisonMatrixOpen && selectedCandidates.length >= 2 && (
        <CandidateComparisonTable
          candidates={selectedCandidates}
          budgetCeiling={businessProfile?.salary_budget || 2000}
          onRemoveCandidate={(candId) => {
            const next = selectedCandidateIds.filter((id) => id !== candId);
            setSelectedCandidateIds(next);
            if (next.length < 2) {
              setIsComparisonMatrixOpen(false);
            }
          }}
          onViewExplanation={(match) => {
            handleViewExplanation(match);
          }}
          onClose={() => setIsComparisonMatrixOpen(false)}
        />
      )}

      {/* Screens 7 & 8: Detailed Candidate View & Explainable AI Decision Card */}
      <CandidateDetailModal
        isOpen={!!activeExplanationMatch}
        onClose={() => setActiveExplanationMatch(null)}
        match={activeExplanationMatch}
        explanation={explanationData}
        isLoadingExplanation={loadingExplanation}
      />
    </div>
  );
}

export const dynamic = "force-dynamic";

export default function RankedResultsDashboard() {

  return (
    <Suspense
      fallback={
        <div className="min-h-[75vh] flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}
