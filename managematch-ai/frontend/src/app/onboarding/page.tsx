"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Zap } from "lucide-react";
import { analyzeRequirements, calculateMatches } from "@/lib/api";

export default function OnboardingWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  
  const [formData, setFormData] = useState({
    name: "",
    industry: "",
    stage: "Seed",
    location: "",
    employees: "",
    goals: "",
    challenges: "",
    raw_preferences: "",
    budget: "",
  });

  const loadDemoPreset = () => {
    setFormData({
      name: "FashionCart",
      industry: "E-Commerce",
      stage: "Growth",
      location: "Lahore, Pakistan",
      employees: "12",
      goals: "Establish automated lifecycle email/SMS flows, Reduce CAC by 35%",
      challenges: "High customer acquisition cost (CAC) on Meta ads and poor retention after first order.",
      raw_preferences: "Need an aggressive growth leader who has scaled D2C apps in emerging markets without wasting budget.",
      budget: "2000"
    });
  };

  const handleNext = () => setStep(2);
  const handleBack = () => setStep(1);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      setLoadingText("Analyzing business needs & extracting key criteria...");
      // Step 1: AI Requirements Extraction
      const analyzeRes = await analyzeRequirements({
        goals: formData.goals,
        challenges: formData.challenges,
        raw_preferences: formData.raw_preferences
      });
      
      console.log("Analyzed Data:", analyzeRes.data);

      setLoadingText("Evaluating candidate pool against 6 deterministic fit factors...");
      
      // We would normally create a business object in DB here and use its ID.
      // For this hackathon demo, we will use a seeded business ID matching our presets.
      // Let's use 'biz_01' which closely matches the FashionCart preset (QuickCart PK).
      const businessId = "biz_01"; 

      // Step 2: Calculate Deterministic Matches
      const matchesRes = await calculateMatches(businessId);
      
      if (matchesRes.success) {
        // Hydrate global state or simply push router with query param
        router.push(`/results?bizId=${businessId}`);
      }
    } catch (error) {
      console.error(error);
      alert("An error occurred during analysis.");
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-8"></div>
        <h2 className="text-2xl font-semibold text-white mb-2">{loadingText}</h2>
        <p className="text-slate-400">Please wait while ManageMatch AI works.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 md:p-12 max-w-4xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Business Profile</h1>
          <p className="text-slate-400">Tell us about your startup to find the perfect operational leader.</p>
        </div>
        <button 
          onClick={loadDemoPreset}
          className="flex items-center gap-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 px-4 py-2 rounded-lg border border-emerald-500/30 transition-all font-medium text-sm"
        >
          <Zap className="w-4 h-4" /> Load FashionCart Demo
        </button>
      </div>

      <div className="bg-glass p-8 rounded-2xl">
        <form onSubmit={step === 1 ? (e) => { e.preventDefault(); handleNext(); } : handleSubmit} className="space-y-6">
          {step === 1 ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
              <h2 className="text-xl font-semibold border-b border-white/10 pb-2">1. Basic Information</h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Company Name</label>
                  <input required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="e.g. FashionCart" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Industry</label>
                  <input required value={formData.industry} onChange={e => setFormData({...formData, industry: e.target.value})} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="e.g. E-Commerce" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Stage</label>
                  <select value={formData.stage} onChange={e => setFormData({...formData, stage: e.target.value})} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500">
                    <option value="Early/Idea">Early/Idea</option>
                    <option value="Seed">Seed</option>
                    <option value="Growth">Growth</option>
                    <option value="Scale">Scale</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Employee Count</label>
                  <input required value={formData.employees} onChange={e => setFormData({...formData, employees: e.target.value})} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="e.g. 12" />
                </div>
              </div>
              <div className="flex justify-end pt-4">
                <button type="submit" className="bg-emerald-500 hover:bg-emerald-400 text-obsidian px-6 py-3 rounded-lg font-bold transition-all">Next Step</button>
              </div>
            </div>
          ) : (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
              <h2 className="text-xl font-semibold border-b border-white/10 pb-2">2. Business Needs</h2>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Primary Goals</label>
                <textarea required value={formData.goals} onChange={e => setFormData({...formData, goals: e.target.value})} rows={3} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="What are you trying to achieve in the next 6 months?" />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Operational Bottlenecks / Challenges</label>
                <textarea required value={formData.challenges} onChange={e => setFormData({...formData, challenges: e.target.value})} rows={3} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="What is currently slowing you down?" />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Ideal Candidate Preferences</label>
                <textarea required value={formData.raw_preferences} onChange={e => setFormData({...formData, raw_preferences: e.target.value})} rows={2} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="Describe the kind of leader you need in your own words." />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Monthly Budget Ceiling (USD)</label>
                <input required type="number" value={formData.budget} onChange={e => setFormData({...formData, budget: e.target.value})} className="w-full bg-obsidian border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500" placeholder="e.g. 2000" />
              </div>

              <div className="flex justify-between pt-4">
                <button type="button" onClick={handleBack} className="px-6 py-3 rounded-lg font-medium text-slate-300 hover:bg-white/5 transition-all">Back</button>
                <button type="submit" className="bg-emerald-500 hover:bg-emerald-400 text-obsidian px-6 py-3 rounded-lg font-bold transition-all flex items-center gap-2">
                  <Zap className="w-4 h-4" /> Analyze & Find Matches
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
