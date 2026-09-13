"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Zap,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  CheckCircle2,
  Layers,
  BarChart3,
  Award,
  Check,
  ChevronRight,
} from "lucide-react";

export default function LandingPage() {
  const [activeFactor, setActiveFactor] = useState<string | null>(null);

  const teaserFactors = [
    { label: "Industry Fit", score: 94, detail: "Deep apparel e-commerce domain expertise with 3+ years in direct-to-consumer." },
    { label: "Stage Fit", score: 95, detail: "Navigated 2 previous startups from seed to growth scaling ($1M to $10M GMV)." },
    { label: "Skills Match", score: 92, detail: "Mastery in Supply Chain, Shopify Plus, 3PL logistics, and Lean Inventory." },
    { label: "Scale Experience", score: 90, detail: "Managed warehouse teams scaling from 12 to 65 personnel." },
    { label: "Budget Alignment", score: 96, detail: "$1,850/mo expectation fits well within $2,000/mo ceiling (+7.5% margin)." },
    { label: "Working Model", score: 90, detail: "Full remote capability matching the company's distributed workflow." },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* 1. HERO SECTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12 pb-16 md:pt-20 md:pb-24">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          {/* Eyebrow Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold uppercase tracking-wider border border-indigo-200/80 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>⚡ AI-Powered Executive Decision Support</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight text-slate-900 leading-[1.1]">
            Find the Vetted Manager Your Business Actually Needs.
          </h1>

          {/* Supporting Copy */}
          <p className="text-base sm:text-lg md:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto">
            BizMatch AI analyzes your specific stage, goals, operational bottlenecks, and compensation constraints to match you with vetted operators—backed by 6-factor deterministic scoring and explainable decision cards.
          </p>

          {/* Dual CTAs (Side by side on desktop, stacked on mobile) */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3.5 pt-2">
            <Link
              href="/match"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-7 py-3.5 rounded-lg font-semibold text-sm transition-all shadow-sm hover:shadow hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2"
            >
              <span>Start Needs Assessment</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/match?demo=true"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white hover:bg-slate-100 text-slate-800 px-6 py-3.5 rounded-lg font-semibold text-sm border border-slate-300 transition-all shadow-sm hover:shadow hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500"
            >
              <Zap className="w-4 h-4 text-amber-600" />
              <span>⚡ Load FashionCart Demo Scenario</span>
            </Link>
          </div>

          {/* Trust Badges */}
          <div className="pt-4 flex flex-wrap items-center justify-center gap-y-2 gap-x-6 text-xs text-slate-500 font-medium">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600" /> 100% Deterministic Core
            </span>
            <span className="flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-indigo-600" /> Grounded Gemini Synthesis
            </span>
            <span className="flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4 text-blue-600" /> Founder Decision-Support
            </span>
          </div>
        </div>

        {/* 2. INTERACTIVE TEASER CANDIDATE CARD */}
        <div className="mt-12 md:mt-16 max-w-4xl mx-auto">
          <div className="text-center mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Interactive Preview · Live Deterministic Engine Output
            </span>
          </div>

          <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm hover:shadow-md transition-all p-6 sm:p-8">
            {/* Candidate Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-sm shrink-0">
                  SK
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-slate-900">Sarah Khan</h3>
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                      Top Recommendation
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 font-medium mt-0.5">
                    Operations &amp; Supply Chain Lead · 7 yrs experience · Lahore, Pakistan
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Rate: <strong className="text-slate-900 font-semibold">$1,850/mo</strong> (Within $2,000 budget)
                  </p>
                </div>
              </div>

              {/* Overall Score Pill */}
              <div className="flex sm:flex-col items-center sm:items-end justify-between shrink-0">
                <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold text-sm">
                  <Award className="w-4 h-4 text-emerald-600" />
                  <span>92.8% Overall Fit</span>
                </div>
                <span className="text-[11px] text-slate-400 mt-1 hidden sm:block">Deterministic 6-Factor</span>
              </div>
            </div>

            {/* 6-Factor Breakdown Grid */}
            <div className="mt-6">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  6-Factor Deterministic Breakdown (Hover for rationale)
                </span>
                <span className="text-[11px] text-indigo-600 font-medium hidden sm:inline">
                  Interactive weights applied
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {teaserFactors.map((f) => (
                  <div
                    key={f.label}
                    onMouseEnter={() => setActiveFactor(f.label)}
                    onMouseLeave={() => setActiveFactor(null)}
                    className={`p-3 rounded-lg border transition-all cursor-pointer ${
                      activeFactor === f.label
                        ? "bg-indigo-50/60 border-indigo-300 shadow-sm"
                        : "bg-slate-50 border-slate-200/80 hover:bg-slate-100/70"
                    }`}
                  >
                    <div className="flex items-center justify-between text-xs mb-1.5">
                      <span className="font-semibold text-slate-700">{f.label}</span>
                      <span className="font-bold text-slate-900">{f.score}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-indigo-600 rounded-full transition-all duration-500"
                        style={{ width: `${f.score}%` }}
                      />
                    </div>
                    {activeFactor === f.label && (
                      <p className="mt-2 text-[11px] text-slate-600 leading-snug animate-fadeIn">
                        {f.detail}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Executive Summary Card Snippet */}
            <div className="mt-6 p-4 rounded-lg bg-emerald-50/60 border border-emerald-200/70 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <p className="text-xs text-slate-700 leading-relaxed">
                  <strong className="text-slate-900 font-semibold">Strategic Fit Verdict:</strong> High alignment for FashionCart&apos;s inventory sync and warehouse bottleneck. Proven experience reducing order fulfillment times by 40%.
                </p>
              </div>
              <Link
                href="/match?demo=true"
                className="shrink-0 text-xs font-semibold text-indigo-700 hover:text-indigo-900 flex items-center gap-1"
              >
                <span>Run Full Match</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3. WHY TRADITIONAL HIRING FAILS FOUNDERS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold uppercase tracking-wider border border-slate-200">
            <Layers className="w-3.5 h-3.5 text-indigo-600" />
            <span>The Strategic Challenge</span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
            Why Traditional Hiring Fails Founders
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Standard job boards reward CV inflation and keywords. BizMatch AI is built for operational bottlenecks and stage-fit precision.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {/* Traditional Job Portals */}
          <div className="bg-white p-6 sm:p-8 rounded-xl border border-rose-200 shadow-sm">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <span className="text-xs uppercase tracking-wider font-semibold text-rose-600">The Status Quo</span>
                <h3 className="text-lg font-bold text-slate-900 mt-0.5">Traditional Job Portals</h3>
              </div>
              <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center font-bold text-xs">
                ✕
              </div>
            </div>
            <ul className="mt-5 space-y-3 text-xs sm:text-sm text-slate-600">
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold">•</span>
                <span>Hundreds of unvetted CVs with generic keyword stuffing.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold">•</span>
                <span>No stage awareness: candidates from corporations struggle in early-stage chaos.</span>
              </li>
              <li className="flex items-start gap-2.5">
                <span className="text-rose-500 font-bold">•</span>
                <span>Founders spend 40+ hours interviewing mismatched profiles.</span>
              </li>
            </ul>
          </div>

          {/* BizMatch AI */}
          <div className="bg-white p-6 sm:p-8 rounded-xl border border-indigo-200 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-50 -z-0 rounded-bl-full" />
            <div className="relative z-10">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <div>
                  <span className="text-xs uppercase tracking-wider font-semibold text-indigo-600">The Solution</span>
                  <h3 className="text-lg font-bold text-slate-900 mt-0.5">BizMatch AI Decision Engine</h3>
                </div>
                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">
                  ✓
                </div>
              </div>
              <ul className="mt-5 space-y-3 text-xs sm:text-sm text-slate-600">
                <li className="flex items-start gap-2.5">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span><strong>Deterministic 6-Factor Engine:</strong> Transparent mathematical scoring without black-box bias.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span><strong>Grounded Gemini Synthesis:</strong> Explainable cards detailing strengths, risks, and missing criteria.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span><strong>Executive Trade-off Matrix:</strong> Instant side-by-side comparison of top candidates.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* 4. THE 6 EVALUATION PILLARS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200 bg-white">
        <div className="text-center max-w-3xl mx-auto mb-12 space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold uppercase tracking-wider border border-indigo-200">
            <BarChart3 className="w-3.5 h-3.5 text-indigo-600" />
            <span>Deterministic Model</span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
            The 6 Deterministic Evaluation Pillars
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">
            Every manager is scored through 6 weighted factors to guarantee objective fit.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {[
            { title: "Industry Relevance (20%)", desc: "Domain expertise and verified knowledge in your specific sector." },
            { title: "Stage Fit (20%)", desc: "Experience at your business lifecycle phase (Seed, Growth, or Scaling)." },
            { title: "Skills Match (20%)", desc: "Direct coverage of your critical operational and functional requirements." },
            { title: "Scale Experience (15%)", desc: "Proven track record managing team sizes and order volume comparable to your trajectory." },
            { title: "Budget Alignment (15%)", desc: "Mathematical evaluation against your monthly compensation ceiling." },
            { title: "Working Model (10%)", desc: "Alignment with remote, hybrid, or on-site operational structures." },
          ].map((item, idx) => (
            <div key={idx} className="p-5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors">
              <span className="text-xs font-bold text-indigo-600">0{idx + 1}</span>
              <h4 className="text-sm font-bold text-slate-900 mt-1">{item.title}</h4>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 5. CTA BANNER */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-slate-200">
        <div className="bg-slate-900 text-white rounded-2xl p-8 sm:p-12 text-center max-w-4xl mx-auto shadow-md relative overflow-hidden">
          <div className="relative z-10 space-y-6">
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold tracking-tight">
              Ready to find the operator your business needs?
            </h2>
            <p className="text-slate-300 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
              Start your requirements assessment or inspect the pre-seeded FashionCart scenario with live backend scoring in seconds.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Link
                href="/match"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-semibold text-sm transition-all shadow-sm"
              >
                <span>Start Assessment</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/match?demo=true"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-lg font-semibold text-sm border border-white/20 transition-all"
              >
                <Zap className="w-4 h-4 text-amber-400" />
                <span>Load FashionCart Demo</span>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
