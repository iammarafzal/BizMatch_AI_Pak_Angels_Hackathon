"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, AlertTriangle, XCircle, ArrowLeft, Loader2 } from "lucide-react";
import Link from "next/link";
import { getCandidateExplanation, getManagers } from "@/lib/api";
import { MatchRecord, Manager } from "@/lib/types";

export default function ResultsDashboard() {
  const searchParams = useSearchParams();
  const bizId = searchParams.get("bizId");
  
  const [managers, setManagers] = useState<Manager[]>([]);
  const [matches, setMatches] = useState<MatchRecord[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [selectedMatch, setSelectedMatch] = useState<MatchRecord | null>(null);
  const [aiExplanation, setAiExplanation] = useState<{strengths: string[], concerns: string[], missing_requirements: string[], verdict: string} | null>(null);
  const [loadingAi, setLoadingAi] = useState(false);

  useEffect(() => {
    async function loadData() {
      if (!bizId) return;
      try {
        // Fetch managers to display details
        const mgrsRes = await getManagers();
        setManagers(mgrsRes);

        // Fetch deterministic matches
        // In a real app we'd fetch the saved matches from DB using bizId
        // For the demo, we call the calculation endpoint again to get the fresh data
        const res = await fetch(`http://localhost:8000/api/matches/calculate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ business_id: bizId }),
        });
        const data = await res.json();
        
        if (data.success) {
          setMatches(data.data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [bizId]);

  const handleSelectCandidate = async (match: MatchRecord) => {
    setSelectedMatch(match);
    setAiExplanation(null);
    
    if (!match.qualitative_analysis) {
      setLoadingAi(true);
      try {
        const res = await getCandidateExplanation(match.business_id, match.manager_id);
        if (res.success) {
          setAiExplanation(res.data);
        }
      } catch (err) {
        console.error("Failed to load AI explanation", err);
      } finally {
        setLoadingAi(false);
      }
    } else {
      setAiExplanation(match.qualitative_analysis);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-emerald-500" />
      </div>
    );
  }

  const selectedManager = managers.find(m => m.id === selectedMatch?.manager_id);

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto">
      <div className="mb-8 flex items-center gap-4">
        <Link href="/onboarding" className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white">Recommended Managers</h1>
          <p className="text-slate-400">Ranked deterministically by 6-factor overlap.</p>
        </div>
      </div>

      <div className="grid lg:grid-cols-12 gap-8">
        {/* Left Column: Ranked Candidates */}
        <div className="lg:col-span-5 space-y-4">
          {matches.map((match) => {
            const mgr = managers.find(m => m.id === match.manager_id);
            if (!mgr) return null;
            
            const isSelected = selectedMatch?.id === match.id;
            
            return (
              <div 
                key={match.id} 
                onClick={() => handleSelectCandidate(match)}
                className={`p-5 rounded-xl cursor-pointer transition-all border ${isSelected ? 'bg-white/10 border-emerald-500/50 shadow-lg shadow-emerald-500/10' : 'bg-glass border-white/10 hover:border-white/20'}`}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="font-semibold text-lg text-white">{mgr.name}</h3>
                    <p className="text-sm text-slate-400">{mgr.role_title}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-emerald-400">{match.overall_score}%</span>
                    <p className="text-xs text-slate-500 uppercase font-semibold">Match Score</p>
                  </div>
                </div>
                
                {/* Progress Bars */}
                <div className="space-y-3 mt-4">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-16 text-slate-400">Skills</span>
                    <div className="flex-grow h-1.5 bg-obsidian rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-500 rounded-full" style={{width: `${match.factor_scores.skills}%`}}></div>
                    </div>
                    <span className="w-8 text-right font-mono">{match.factor_scores.skills}%</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-16 text-slate-400">Stage</span>
                    <div className="flex-grow h-1.5 bg-obsidian rounded-full overflow-hidden">
                      <div className="h-full bg-violet-500 rounded-full" style={{width: `${match.factor_scores.stage}%`}}></div>
                    </div>
                    <span className="w-8 text-right font-mono">{match.factor_scores.stage}%</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-16 text-slate-400">Industry</span>
                    <div className="flex-grow h-1.5 bg-obsidian rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 rounded-full" style={{width: `${match.factor_scores.industry}%`}}></div>
                    </div>
                    <span className="w-8 text-right font-mono">{match.factor_scores.industry}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Deep Dive & AI Decision Card */}
        <div className="lg:col-span-7">
          {selectedMatch && selectedManager ? (
            <div className="bg-glass border border-white/10 rounded-2xl p-6 sticky top-24">
              <div className="border-b border-white/10 pb-6 mb-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedManager.name}</h2>
                    <p className="text-emerald-400 font-medium">{selectedManager.role_title}</p>
                  </div>
                  <div className="text-right text-sm">
                    <p className="text-slate-400">Expected Rate</p>
                    <p className="text-white font-semibold">${selectedManager.monthly_rate_usd}/mo</p>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {selectedManager.core_skills.map(skill => (
                    <span key={skill} className="px-2.5 py-1 rounded-full bg-white/5 text-xs text-slate-300 border border-white/10">{skill}</span>
                  ))}
                </div>
              </div>

              <h3 className="font-semibold text-lg text-white mb-4">AI Decision Support</h3>
              
              {loadingAi ? (
                <div className="py-12 flex flex-col items-center justify-center text-center">
                  <Loader2 className="w-8 h-8 animate-spin text-cyan-500 mb-4" />
                  <p className="text-slate-400 text-sm">Gemini is synthesizing a qualitative audit<br/>based on deterministic overlaps...</p>
                </div>
              ) : aiExplanation ? (
                <div className="space-y-6">
                  {/* Strengths */}
                  <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4">
                    <h4 className="flex items-center gap-2 text-emerald-400 font-semibold mb-3">
                      <CheckCircle2 className="w-5 h-5" /> Verified Strengths
                    </h4>
                    <ul className="space-y-2">
                      {aiExplanation.strengths.map((s: string, i: number) => (
                        <li key={i} className="text-sm text-slate-200 flex items-start gap-2">
                          <span className="text-emerald-500 mt-0.5">•</span> {s}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Concerns */}
                  <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
                    <h4 className="flex items-center gap-2 text-amber-400 font-semibold mb-3">
                      <AlertTriangle className="w-5 h-5" /> Potential Watchpoints
                    </h4>
                    <ul className="space-y-2">
                      {aiExplanation.concerns.map((c: string, i: number) => (
                        <li key={i} className="text-sm text-slate-200 flex items-start gap-2">
                          <span className="text-amber-500 mt-0.5">•</span> {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  {/* Missing */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                    <h4 className="flex items-center gap-2 text-slate-400 font-semibold mb-3">
                      <XCircle className="w-5 h-5" /> Missing Requirements
                    </h4>
                    <ul className="space-y-2">
                      {aiExplanation.missing_requirements.map((m: string, i: number) => (
                        <li key={i} className="text-sm text-slate-400 flex items-start gap-2">
                          <span className="text-slate-600 mt-0.5">•</span> {m}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Verdict */}
                  <div className="mt-6 p-5 bg-gradient-to-br from-obsidian to-slate-900 border border-white/10 rounded-xl shadow-inner">
                    <h4 className="text-xs uppercase tracking-wider font-bold text-slate-500 mb-2">Synthesis Verdict</h4>
                    <p className="text-sm text-slate-300 italic">&quot;{aiExplanation.verdict}&quot;</p>
                  </div>
                </div>
              ) : (
                <p className="text-slate-500 text-sm">Select a candidate to view AI analysis.</p>
              )}
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-12 bg-white/5 border border-white/5 rounded-2xl border-dashed">
              <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mb-4">
                <CheckCircle2 className="w-8 h-8 text-slate-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-400 mb-2">Select a Manager</h3>
              <p className="text-slate-500 text-sm max-w-sm">
                Click on a ranked candidate card to load their profile and generate an explainable AI decision support memo.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
